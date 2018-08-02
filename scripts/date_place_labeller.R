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

### OLD VERSION

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
# Jacob's Functions
# ====================================

### loading RDS data file 'metadata_table.rds'

tua_data <- readRDS(file='data/metadata_table.rds')

### defining hierachical date labeller

NA_indices <- c()  # vector containing NA indices

label_date <- function(article_data) {  # adds event dates to new 'event_date' column
  #processed_data <- try_specific_date(article_data) ...TBD
  
  # fixes NA_indices in absence of phase 1
  NA_indices <<- 1:nrow(article_data)
  
  # phase 2: weekdays
  processed_data <- try_function(getEventDate, article_data)
  
  # phase 3: keywords
  processed_data <- try_function(date_from_keyword, processed_data)
  
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
  df$event_date <- as.Date(df$event_date, origin = as.Date("1970-01-01"))
  NA_indices <<- temp_indices
  return (df)
}

# phase 1
# TBD

# phase 2
getEventDate <- function(tua, pdate) {
  # write this as a helper function
  pdate_weekday_number <- weekdayNumber(pdate)
  event_weekday_number <- return_days(paste(tua, sep = '', collapse = ''))
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

new_data <- label_date(tua_data)
# write_rds(new_data, path = "tuas_with_ids.rds")
