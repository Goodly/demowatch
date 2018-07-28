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

col_names <- c("task", "contributor", all_q)
all_answers <- matrix(0, ncol = length(all_q) + 2, 
                      nrow = nrow(tasks_and_contributors))
all_answers[, 1:2] <- as.matrix(tasks_and_contributors)
colnames(all_answers) <- col_names

### formatter function

answer_formatter <- function(tbl_row) {
  ### retrieve task and contributor
  task <- tasks_and_contributors[[tbl_row, 1]]
  contributor <- tasks_and_contributors[[tbl_row, 2]]
  
  ### access the answers
  sub_table <- grouped_dat %>%
    filter(task_pybossa_id == task & contributor_id == contributor)
  sub_answers <- as.data.frame(t(sub_table[, 3:4]))
  
  ### transform answers tall to wide
  columns <- unlist(sub_answers[1, ])
  sub_answers <- as.data.frame(sub_answers[c(FALSE, TRUE), ])
  colnames(sub_answers) <- columns

  ### fill in columns for missing questions
  missing_q <- setdiff(all_q, columns)
  missing_ans <- as.data.frame(matrix(0, ncol = length(missing_q)))
  colnames(missing_ans) <- missing_q
  
  ### bind to answered questions and reorder
  all_q_ans <- cbind(sub_answers, missing_ans)[, all_q]
  return(all_q_ans)
}

all_q_ans_tbl <- answer_formatter(1)

for (i in 2:nrow(tasks_and_contributors)) {
  ### format the answers
  print(i)
  ans_tbl <- answer_formatter(i)
  
  ### bind to the first row
  all_q_ans_tbl <- rbind(all_q_ans_tbl, ans_tbl)
}
