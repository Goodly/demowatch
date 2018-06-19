library(readr)
library(dplyr)

### set your work directory
dir <- "~/df-canonicalization"
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
           "info_article_text.x", 
           "info_article_metadata_city",
           "info_article_metadata_date_published"))

### source functions from Nick's script
source("scripts/Day2Dates.R")
