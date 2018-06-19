library(readr)
library(dplyr)

# set your work directory
dir <- "~/goodly/"

# Read in data
dat <- read_csv(paste0(dir, 
                       "33_dfcrowd1dh_task_run_csv/dfcrowd1dh_task_run.csv"))
metadata_dat <- read_csv(paste0(dir, "dfcrowd1dh_task.csv"))

### Group task runs by task ID and choose one, merge in publication date
training_dat <- dat %>% 
  group_by(task_id) %>%
  slice(1) %>% 
  select(c("task_id", "info_article_text", "info_article_id"))

training_dat
### Extracting metadata dates and text

metadata_date <- 
text <- dat[, 7]