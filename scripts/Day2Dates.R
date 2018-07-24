#####################################
#Some FUNCTIONS for DATE EXTRACTION
#####################################
#This function takes a formatted date as Y-m-d and returns weekday
day_from_date <- function(adate = NULL) {
  if (!is.null(adate)) {
    day_list <- c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                  "Saturday")
    dow <- try(which(grepl(weekdays(as.Date(adate, "%m-%d-%y")), day_list)), silent=TRUE)
    if(inherits(dow, "try-error")) dow <- NA
    return(dow)
  }
}

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

# Function takes weekday difference between article_date and text_date and
# calculates approximate date.
day_in_text <- function(article_day, aday, pdate) {
  if(!is.na(pdate)){
    date_diff <- aday - pdate
    if (date_diff > 0) {
      out <- as.Date(article_day, "%m-%d-%y") - date_diff
    } else {
      dd <- ifelse(date_diff != 0, date_diff + 7, 0)
      out <- as.Date(article_day, "%m-%d-%y") - dd
    }
  } else{
    out <- try(as.Date(article_day, "%m-%d-%y") - 1, silent=TRUE)
    if(inherits(out, "try-error")) out <- NA
  }
  return(out)
}

##############################################
#NOW, to extract DATES from tua text daynames
##############################################
library(lubridate)
#library(dplyr)
library(readr)

all3clean$article_date<-as.character(all3clean$article_date)

published_day <-  sapply(all3clean$article_date, day_from_date)

text_day <- sapply(all3clean$tua_svo, return_days)
guessing_date_in_text <- mapply(function(a,b,c)
  day_in_text(article_day=a, aday=b, pdate=c),
  a=all3clean$article_date,
  b=published_day,
  c=text_day,
  SIMPLIFY=FALSE)

guessing_date_in_text <- lapply(guessing_date_in_text, function(x) as.character(x))
guessing_date_in_text <- c(do.call(rbind, guessing_date_in_text))
all3clean$text_date <- guessing_date_in_text
all3clean$text_date <- as.Date(all3clean$text_date, "%Y-%m-%d")
View(unique(all3clean$text_date))
