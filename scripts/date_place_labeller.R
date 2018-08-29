library(readr)
library(dplyr)
library(lubridate)
### set your work directory
#dir <- "~/df-canonicalization"
# dir <- "/Users/aaronhoby/Documents/BerkeleySem3/DecidingForce/df-canonicalization"
# setwd(dir)

### read in data
# dat <- read_csv("data/textthresher/dfcrowd1dh_task_run.csv")
# metadata_dat <- read_csv("data/textthresher/dfcrowd1dh_task.csv")
# metadata_with_tua <- read_csv('data/textthresher/DF_Crowd1.0_DataHunt-TUAS.csv')
# 
# ### group task runs by task ID and choose one, merge in publication date and location
# training_dat <- dat %>% 
#   group_by(task_id) %>%
#   slice(1) %>% 
#   inner_join(metadata_dat, by = c("task_id" = "id")) %>%
#   select(c("task_id", 
#            "info_article_article_number",
#            "info_article_text.x",
#            "info_highlights_0_case_number",
#            "info_article_metadata_city",
#            "info_article_metadata_date_published"))
#write_csv(training_dat, "data/metadata_table.csv")

### source functions from Nick's script : helper function
# This function takes some text and returns the position on the weekday list
# So return_days("Monday Tuesday Friday")
# will return 2 (for Monday)
return_days <- function(text) {
  if(!is.na(text)) {
    if(is.character(text)) {
      day_list <- c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                    "Saturday")
      res <- as.numeric(which(sapply(day_list, grepl, text, ignore.case = TRUE)))
      if (length(res) == 0) {
        res <- NA
      } else {
        res<-res[1] # we can add more handling here to deal with multiple weekday mentions
      }
    }
  } else res <- NA
  return(res)
}

## helper functions
#' @description Converts date to numbered weekday
#' @param date_object Some date object or sequence of date objects
#' @return Integer representing the date_object's day of the week.
#' ie: 2018-06-23 is a Saturday, so it's weekday number is 7.
weekdayNumber <- function(date_object) {
  day_list <- c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday")
  return (match(weekdays(date_object), day_list))
}

#' @description Based on weekday mentioned in article text as well as publishing date,
#' returns the YYYY-MM-DD date of the event described in the TUA
#' @param article_data data.frame containing columns 'article_text' and 'date_published'.
#' Values in 'date_published' must be Date objects.
#' @return Original data.frame, with new column 'event_date'.
#' Values are date objects representing the date of the event described in the article
getEventDate <- function(article_data) {
  pdate_weekday_number <- weekdayNumber(article_data$date_published)
  event_weekday_number <- t(data.frame(lapply(article_data$article_text, return_days)))
  date_diff <- pdate_weekday_number - event_weekday_number
  numeric_diff <- ifelse(date_diff >= 0, date_diff,  # >= 0: date_diff; < 0: add 7; NA: leave as is
         ifelse(date_diff < 0, date_diff + 7, NA))  # NOTE: ifelse is used for vectorizaiton
  event_dates <- article_data$date_published - numeric_diff
  return (cbind(article_data, event_date = event_dates))
}

### adjustments
# names(training_dat)[3] <- 'article_text'
# names(training_dat)[6] <- 'date_published'
# 
# train_with_event <- getEventDate(training_dat) # returns NA for date published if no weekday found
# 
# ### loading RDS data file 'metadata_table.rds'
# 
# tua_data <- readRDS(file='data/metadata_table.rds')

### defining hierachical date labeller

NA_indices <- c()  # vector containing NA indices

label_date <- function(article_data) {  # adds event dates to new 'event_date' column
  # fixes initial NA_indices
  NA_indices <<- 1:nrow(article_data)
  
  # phase 1 : specific dates
  processed_data <- try_function(getSpecificDate, article_data)
  
  # phase 2: weekdays
  processed_data <- try_function(getEventDate, processed_data)
  
  # phase 3: keywords
  processed_data <- try_function(date_from_keyword, processed_data)
  
  # # phase 3 and 1/2: stanford nlp
  # processed_data <- try_function(stanford_nlp, processed_data)
  
  # phase 4: date published
  processed_data <- try_function(use_pdate, processed_data)
  
  # create unique id's
  processed_data <- addUniqueIDs(processed_data)
  
  return (processed_data)
}

# ====================================
# Helper Functions
# ====================================

### Base Hierarchy Function

try_function <- function(func, df) {
  # null check
  if (is.null(NA_indices)) return (df)
  temp_indices <- c()
  for (i in NA_indices) {
    val <- func(df[i, 'TUA'], df[[i, 'date_published']])
    if (!is.na(val)) {
      df[i, 'event_date'] <- val
    } else {
      temp_indices <- c(temp_indices, i)
    }
  }
  NA_indices <<- temp_indices
  return (df)
}

# phase 1
getSpecificDate <- function(tua, pdate) {
  if (is.na(pdate)) return (NA)
  matches <- regmatches(tua, regexpr("[[:alpha:]]{3,9}.? [[:digit:]]{1,2}", tua))
  matches <- Filter(validDate, matches)
  if (identical(matches, character(0))) return (NA)
  # if (length(matches) > 1) return ('flag') # DO SOMETHING...probably ask for user to reassess
  splitpoint <- as.numeric(gregexpr(pattern = " ", matches[1]))
  month <- substring(matches[1], 1, last = splitpoint - 1)
  day <- substring(matches[1], splitpoint + 1)
  month <- switch(month, January = "01", Jan. = "01", February = "02", Feb. = "02", March = "03", 
                  Mar. = "03", April = "04", Apr. = "04", May = "05", June = "06", Jun. = "06",
                  July = "07", Jul. = "07", August = "08", Aug. = "08", September = "09", Sept. = "09",
                  October = "10", Oct. = "10", November = "11", Nov. = "11", December = "12", Dec. = "12")
  day <- switch(as.numeric(day), "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",
                "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
                "28", "29", "30", "31")
  if (identical(month(pdate), "12") &  identical(month(pdate), 1)) {
    year <- as.character(year(pdate) - 1)
  } else {
    year <- as.character(year(pdate))
  }
  return (as.Date(paste(year, month, day, sep = '-')))
}

# helper function for phase 1
validDate <- function(match) {
  keywords = "January|Jan.|February|Feb.|March|Mar.|April|Apr.|May|June|Jun.|July|Jul.|August|Aug.
  |September|Sept.|October|Oct.|November|Nov.|December|Dec."
  return (as.logical(sum(grepl(keywords, match))))
}

# phase 2
getEventDate <- function(tua, pdate) {
  # write this as a helper function
  if (is.na(pdate)) return (NA)
  pdate_weekday_number <- weekdayNumber(pdate)
  event_weekday_number <- return_days(paste(tua, sep = '', collapse = ''))
  if (is.na(event_weekday_number)) return (NA)
  date_diff <- pdate_weekday_number - event_weekday_number
  numeric_diff <- ifelse(date_diff > 0, date_diff,  # > 0: date_diff; < 0: add 7; == 0: leave as is
                         ifelse(date_diff < 0, date_diff + 7, 0))  # NOTE: ifelse is used for vectorizaiton
  event_dates <- pdate - numeric_diff
  return (event_dates)
}

weekdayNumber <- function(date_object) {
  day_list <- c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday")
  return (match(weekdays(date_object), day_list))
}

# phase 3
date_from_keyword <- function(text, pdate) {
  # null check
  if (is.na(text)) return (NA)
  
  # creates named vector of keyword matches
  keywords <- c('yesterday', 'a day ago', 'earlier today', 'this morning', 'tomorrow')  # etc
  matches <- sapply(keywords, grepl, text, ignore.case = TRUE)
  
  # edge cases
  if (sum(matches) > 1) return ('flag')  # DO SOMETHING ... possibly create a date range?
  # recommend we review it. shouldn't be common.
  # impute a flag character, then we can just sort by the character and return for review
  if (sum(matches) == 0) return (NA)
  
  # keyword cases
  if (matches['yesterday']) return (pdate - 1)
  if (matches['a day ago']) return (pdate - 1)
  if (matches['earlier today']) return (pdate)
  if (matches['this morning']) return (pdate)
  if (matches['tomorrow']) return (pdate + 1)
  # etc
}

# phase 3 and 1/2
## NOTE: Will need to manually download Stanford NLP, b/c no space on Github
stanford_nlp <- function(tua, pdate) {
  setwd("/Users/aaronhoby/Documents/BerkeleySem3/DecidingForce/df-canonicalization")
  rds <- readRDS("data/metadata_table.rds")
  paste(rds$TUA[3][[1]], collapse= '')
  write("Christmas", file = "data/stanford-corenlp-full-2018-02-27/input.txt")
  ## adjust the following setwd() for your computer
  setwd("/Users/aaronhoby/Documents/BerkeleySem3/DecidingForce/df-canonicalization/data/stanford-corenlp-full-2018-02-27")
  system("java --add-modules java.se.ee -cp '*' -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner -file input.txt")
  library(XML)
  ## adjust the following setwd() for your computer
  setwd("/Users/aaronhoby/Documents/BerkeleySem3/DecidingForce/df-canonicalization")
  relevantDates <- c()
  doc <- xmlTreeParse("data/stanford-corenlp-full-2018-02-27/input.txt.xml", useInternal = TRUE)
  nodes <- getNodeSet(doc, "//NormalizedNER")
  lapply(nodes, function(n) {
    relevantDates <<- c(relevantDates, xmlValue(n))
  })
  relativeHours <- unique(relevantDates[grepl("^PT[[:digit:]]{2,3}H$", relevantDates)])
  relativeHours <- as.numeric(substr(relativeHours, 3, nchar(relativeHours) - 1))
  relativeDays <- unique(relevantDates[grepl("^P[[:digit:]]{1,2}D$", relevantDates)])
  relativeDays <- as.numeric(substr(relativeDays, 2, nchar(relativeDays) - 1))
  offsets <- unique(relevantDates[grepl("^OFFSET P-?[[:digit:]]{1,2}D$", relevantDates)])
  offsets <- as.numeric(substr(offsets, 9, nchar(offsets) - 1))
  relativeWeeks <- unique(relevantDates[grepl("^P[[:digit:]]{1,2}W$", relevantDates)])
  relativeWeeks <- as.numeric(substr(relativeWeeks, 2, nchar(relativeWeeks) - 1))
  relativeYears <- unique(relevantDates[grepl("^P[[:digit:]]{1,2}Y$", relevantDates)])
  relativeYears <- as.numeric(substr(relativeYears, 2, nchar(relativeYears) - 1))
  if (!identical(relativeYears, numeric(0))) {
    return (pdate - ceiling(365 * mean(relativeYears)))
  } else if (!identical(relativeWeeks, numeric(0))) {
    return (pdate - ceiling(7 * mean(relativeWeeks)))
  } else if (!identical(offsets, numeric(0))) {
    return (pdate + ceiling(mean(offsets))) 
  } else if (!identical(relativeDays, numeric(0))) {
    return (pdate - ceiling(mean(relativeDays)))
  } else if (!identical(relativeHours, numeric(0))) {
    return (pdate - ceiling(mean(relativeHours)) / 24)
  } else {
    return (NA)
  }
}

# phase 4
use_pdate <- function(tua, pdate) {
  return (pdate)
}

# create unique id's
library(hash)
addUniqueIDs <- function(processed_data) {
  eventMappings <- hash()
  eventIDs <- c()
  count <- 1
  for (i in 1:nrow(processed_data)) {
    id <- paste(processed_data$event_place[i], as.character(processed_data$event_date[i]), sep='')
    idless <- paste(processed_data$event_place[i], as.character(processed_data$event_date[i] - 1), sep='')
    idmore <- paste(processed_data$event_place[i], as.character(processed_data$event_date[i] + 1), sep='')
    if (is.null(names(eventMappings)) | !is.element(id, keys(eventMappings))) {
      eventMappings[[id]] = count; eventMappings[[idless]] = count; eventMappings[[idmore]] = count
      eventIDs <- c(eventIDs, count)
      count <- count + 1
    } else {
      eventIDs <- c(eventIDs, eventMappings[[id]])
    }
  }
  return (cbind(processed_data, ids = eventIDs))
}

# new_data <- label_date(tua_data)
# write_rds(new_data, path = "data/tuas_with_ids.rds")
