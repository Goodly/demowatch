library(readr)
library(dplyr)

### set your work directory
#dir <- "~/df-canonicalization"
dir <- "C:/Users/acobw/Desktop/goodlylabs/df-canonicalization/"
setwd(dir)

### read in data
dat <- read_csv("data/textthresher/dfcrowd1dh_task_run.csv")
metadata_dat <- read_csv("data/textthresher/dfcrowd1dh_task.csv")
metadata_with_tua <- read_csv('data/metadata_with_tua.csv')

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
  numeric_diff <- ifelse(date_diff > 0, date_diff,  # > 0: date_diff; < 0: add 7; == 0: leave as is
         ifelse(date_diff < 0, date_diff + 7, 0))  # NOTE: ifelse is used for vectorizaiton
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
  article_data$event_date[NA_indices] <- training_dat$date_published[NA_indices]
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
