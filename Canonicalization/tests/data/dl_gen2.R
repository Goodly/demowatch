### DIRECTORY
library(readr)
dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

task_id <- as.integer(c(111, 222, 999))
article_number <- as.integer(c(23, 125, 732))
case_number <- as.integer(c(1, 2, 3))
event_place <- as.character(c("Atlanta", "Little Rock", "Seattle"))
date_published <- as.Date(c("2011-10-24", "2011-11-05", "2011-12-16"))
TUA <- I(list(c("October 22"),
         c("Nov. 2"), 
         c("November")))
info_article_text.x <- as.character(c("There was fake blood running in the streets of London Thursday — thanks to an elaborate, 
           and ultimately spectacularly botched stunt by climate change activists. Activists with
           Extinction Rebellion had purchased a decommissioned fire truck on eBay in hopes of spraying
           fake blood on the British Treasury building, but most of it wound up flooding the street, 
           according to reports.",
           "Iraq's Prime Minister Adel Abdul Mahdi has called for dialogue after a third consecutive day
           of deadly anti-government protests in the capital, Baghdad, and several southern cities. In a
           statement quoted by local media on Thursday, Abdul Mahdi's office said the prime minister was 
           'continuing contacts' with protesters in a bid to end the political crisis and
           'return to normal life'.",
           "PARIS —  A civilian employee raged through Paris police headquarters with a knife Thursday,
           stabbing four police colleagues to death before he was shot and killed, French authorities
           said. The man, a technology administrator in the police intelligence unit, launched the attack in
           his office then moved to other parts of the large 19th century building across the street from
           Notre Dame Cathedral."))
file_name <- as.character(c("\"london.txt\"", "\"baghdad.txt\"", "\"paris.txt\""))

my_data <- data.frame(task_id, article_number, case_number, event_place, date_published, TUA, 
                      info_article_text.x, file_name)
names(my_data) <- c("task_id", "article_number", "case_number", "event_place", "date_published", "TUA", 
                    "info_article_text.x", "file_name")
saveRDS(my_data, file = "tests/data/dl_input2.rds")