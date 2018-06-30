library(readr)
library(dplyr)

### set your work directory
#dir <- "~/df-canonicalization"
dir <- "C:/Users/acobw/Desktop/goodlylabs/df-canonicalization/"
setwd(dir)

### read in data
dat <- read_csv("data/textthresher/dfcrowd1dh_task_run.csv")
metadata_dat <- read_csv("data/textthresher/dfcrowd1dh_task.csv")

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
write_csv(training_dat, "data/metadata_table.csv")

### source functions from Nick's script
source("scripts/Day2Dates.R")

#' @description Based on weekday mentioned in article text as well as publishing date,
#' returns the YYYY-MM-DD date of the event described in the article
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

#' @description Converts date to numbered weekday
#' @param date_object Some date object or sequence of date objects
#' @return Integer representing the date_object's day of the week.
#' ie: 2018-06-23 is a Saturday, so it's weekday number is 7.
weekdayNumber <- function(date_object) {
  day_list <- c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday")
  return (match(weekdays(date_object), day_list))
}

names(training_dat)[2] <- 'article_text'
names(training_dat)[4] <- 'date_published'

train_with_event <- getEventDate(training_dat)
