library(jsonlite)
library(readr)
library(dplyr)
library(reshape2)

### JSON processing
dat_json <- read_json("~/Desktop/downloads/dfcrowd1dh-2018-06-21T01.json")
results <- dat_json$results

dim(results)

### CSV processing
dat <- read_csv("~/Desktop/downloads/dfcrowd1dh-2018-06-21T01.csv")

grouped_dat <- dat %>%
  group_by(task_pybossa_id,
           contributor_id,
           topic_number,
           question_number,
           answer_number) %>%
  select(task_pybossa_id,
         contributor_id,
         topic_number,
         question_number,
         answer_number) %>%
  group_by(task_pybossa_id ,
           contributor_id,
           topic_number,
           question_number) %>%
  summarize(answer_list = list(unique(answer_number)))

molten_dat <- melt(grouped_dat,
                   id.vars = c("task_pybossa_id", "contributor_id"))
casted_dat <- dcast()