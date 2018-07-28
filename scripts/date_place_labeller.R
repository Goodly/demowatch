library(readr)
library(dplyr)

### set your work directory
#dir <- "~/df-canonicalization"
dir <- "/Users/aaronhoby/Documents/BerkeleySem3/DecidingForce/df-canonicalization"
setwd(dir)

### read in data
dat <- read_csv("data/textthresher/dfcrowd1dh_task_run.csv")
metadata_dat <- read_csv("data/textthresher/dfcrowd1dh_task.csv")
metadata_with_tua <- read_csv('data/textthresher/DF_Crowd1.0_DataHunt-TUAS.csv')

### group task runs by task ID and choose one, merge in publication date and location
training_dat <- dat %>% 
  group_by(task_id) %>%
  slice(1) %>% 
  inner_join(metadata_dat, by = c("task_id" = "id")) %>%
  select(c("task_id", 
           "info_article_article_number",
           "info_article_text.x",
           "info_highlights_0_case_number",
           "info_article_metadata_city",
           "info_article_metadata_date_published"))
#write_csv(training_dat, "data/metadata_table.csv")

### source functions from Nick's script
source("scripts/Day2Dates.R")

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

### testing on training_dat
names(training_dat)[3] <- 'article_text'
names(training_dat)[6] <- 'date_published'

train_with_event <- getEventDate(training_dat) # returns NA for date published if no weekday found

# ====================================
# Jacob's Tests
# ====================================

"
phase1 specific date
phase2 relative date (weekdays)
phase3 keywords (yesterday, tomorrow, a day ago, etc)
phase4 make guess using pdate as proxy
"

### loading RDS data file 'metadata_table.rds'

tua_data <- readRDS(file='data/metadata_table.rds')

### defining hierachical date labeller

NA_indices <- c()  # vector containing NA indices

label_date <- function(article_data) {  # adds event dates to new 'event_date' column
  processed_data <- try_specific_date(article_data)
  processed_data <- getEventDate(processed_data)
  processed_data <- try_keywords(processed_data)
  processed_data <- try_pdate(processed_data)
  return (processed_data)
}

### phase 3: keywords

try_keywords <- function(df) {
  temp_indices <- c()
  for (i in NA_indices) {
    val <- date_from_keyword(df[i, 'TUA'], df[i, 'date_published'])
    if (!is.na(val)) {
      df[i, 'event_date'] <- val
    } else {
      temp_indices <- c(temp_indices, i)
    }
  }
  NA_indices <<- temp_indices
  return (df)
}

# ====================================
# Aaron's Code
# ====================================

### phase 4: date published

#' @description Last resort method: sets the event described in the article as the
#' publication date.
#' @param article_data data.frame containing columns 'article_text' and 'date_published'.
#' Values in 'date_published' must be Date objects.
#' @return Original data.frame, with new column 'event_date'.
#' Values are date objects representing the date of the event described in the article
try_pdate <- function(article_data) {
  article_data$event_date[NA_indices] <- training_dat$date_published[NA_indices] - 1
  return (article_data)
}

# ====================================
# 
# ====================================

### helper functions

date_from_keyword <- function(text, pdate) { # HOW TO HANDLE MUTLIPLE KEYWORDS BEING FOUND?
  # null check
  if (is.na(text)) return (NA)
  
  # creates named vector of keyword matches
  keywords <- c('yesterday', 'a day ago', 'earlier today', 'this morning', 'tomorrow')  # etc
  matches <- sapply(keywords, grepl, text, ignore.case = TRUE)
  
  # edge cases
  if (sum(matches) > 1) stop()  # DO SOMETHING ... possibly create a date range?
  if (sum(matches) == 0) return (NA)
  
  # keyword cases
  if (matches['yesterday']) return (pdate - 1)
  if (matches['a day ago']) return (pdate - 1)
  if (matches['earlier today']) return (pdate)
  if (matches['this morning']) return (pdate)
  if (matches['tomorrow']) return (pdate + 1)
  # etc
}

alt_date_from_keywords <- function(text, pdate) {
  if (is.na(text)) return (NA)
  inputFile <- file("data/stanford-corenlp-full-2018-02-27/input.txt")
  writeLines(text, inputFile)
  close(inputFile)
  setwd("/Users/aaronhoby/Documents/BerkeleySem3/DecidingForce/df-canonicalization")
  rds <- readRDS("data/metadata_table.rds")
  # paste(rds$TUA[3][[1]], collapse= '')
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
  exactDates <- substr(unique(relevantDates[grepl("[[:digit:]]{4}-[[:digit:]]{2}-[[:digit:]]{2}", relevantDates)]), 1, 10)
  noYearDates <- substr(unique(relevantDates[grepl("[[:alpha:]]{4}-[[:digit:]]{2}-[[:digit:]]{2}", relevantDates)]), 5, 10)
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
  if (!identical(exactDates, character(0))) {
    return (as.Date(ceiling(mean(as.numeric(as.Date(exactDates))))))
  } else if (!identical(noYearDates, character(0))) {
    return (as.Date(ceiling((mean(as.numeric(as.Date(sapply(noYearDates, function(x) paste(substr(pdate, 1, 4), x, sep= '')))))))))
  } else if (!identical(relativeYears, numeric(0))) {
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