### DIRECTORY
library(readr)
dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

task_pybossa_id <- as.integer(c(111, 111, 222, 222))
contributor_id <- as.integer(c(1, 2, 3, 4))
q1 <- as.numeric(c(1, 1, 0, 0))
q2 <- as.numeric(c(0, 0, 1, 1))
q3 <- as.numeric(c(0, 0, 1, 1))
q4 <- as.numeric(c(1, 1, 0, 0))
ids <- as.integer(c(1, 1, 2, 2))

my_data <- data.frame(task_pybossa_id, contributor_id, q1, q2, q3, q4, ids)
names(my_data) <- c("task_pybossa_id", "contributor_id", "0.01.01", "0.01.02", "0.01.03", "0.01.04", "ids")
saveRDS(my_data, file = "tests/data/dl_input6.rds")

# chr, num, factor
q_name <- c('0.01', '0.01', '0.01', '0.01')
test_weights <- as.numeric(c(0.1, 0.1, 0.1, 1.0))
col <- factor(c("0.01.01", "0.01.02", "0.01.03", "0.01.04"))

also_data <- data.frame(q_name, test_weights, col)
names(also_data) <- c("q_name", "weights", "col")
saveRDS(also_data, file="tests/data/dl_weights6.rds")