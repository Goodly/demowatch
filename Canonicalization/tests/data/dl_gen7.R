### DIRECTORY
library(readr)
dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

task_pybossa_id <- as.integer(c(111, 111, 111, 222, 222, 222, 333, 333, 333))
contributor_id <- as.integer(c(1, 2, 3, 4, 5, 6, 7, 8, 9))
q1 <- as.numeric(c(1, 1, 1, 0, 0, 0, 1, 1, 1))
q2 <- as.numeric(c(1, 0, 0, 0, 1, 1, 1, 0, 0))
q3 <- as.numeric(c(0, 0, 1, 1, 1, 0, 0, 0, 1))
q4 <- as.numeric(c(1, 1, 1, 0, 0, 0, 1, 1, 1))
ids <- as.integer(c(1, 1, 1, 2, 2, 2, 3, 3, 3))

my_data <- data.frame(task_pybossa_id, contributor_id, q1, q2, q3, q4, ids)
names(my_data) <- c("task_pybossa_id", "contributor_id", "0.01.01", "0.01.02", "0.01.03", "0.01.04", "ids")
saveRDS(my_data, file = "tests/data/dl_input7.rds")