library(readr)
library(dplyr)
library(reshape2)

### CSV processing
dat <- read_csv("~/df-canonicalization/data/textthresher/dfcrowd1dh-2018-06-21T01.csv")

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

grouped_dat$question_number <- sapply(grouped_dat$question_number, 
                                      function(x) {if (x < 10) {
                                        return(paste0(0, x))
                                        } else {
                                          return(as.character(x))}})

grouped_dat <- grouped_dat %>% mutate(question_number = paste(topic_number, 
                                                              question_number, 
                                                              sep = "."))
grouped_dat <- grouped_dat[, c(1, 2, 4, 5)]

all_q <- sort(unique(grouped_dat$question_number))
tasks_and_contributors <- grouped_dat %>%
  group_by(task_pybossa_id, contributor_id) %>%
  summarize() %>% 
  na.omit()


for (i in 1:nrow(tasks_and_contributors)) {
  task <- tasks_and_contributors[[i, 1]]
  contributor <- tasks_and_contributors[[i, 2]]
  
  sub_table <- grouped_dat %>%
    filter(task_pybossa_id == task & contributor_id == contributor)
  sub_answers <- as.data.frame(t(sub_table[, 3:4]))
  
  colnames(sub_answers) <- unlist(sub_answers[1, ])
  sub_answers <- sub_answers[-1, ]
}
