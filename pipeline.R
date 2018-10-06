### INPUT -> PROCESS -> OUTPUT PIPELINE ###
library(readr)

dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

### INPUT
### load raw data
raw_metadata <- read_csv("data/textthresher/dfcrowd1dh_task.csv")
raw_tua <- read_csv("data/textthresher/DF_Crowd1.0_DataHunt-TUAS.csv")
raw_taskruns <- read_csv("data/textthresher/dfcrowd1dh_task_run.csv")
raw_qs_ans <- read_csv("data/textthresher/dfcrowd1dh-2018-06-21T01.csv")
scheme_qs <- read_csv("data/scheme_q_types.csv")

### PROCESS
### source and call functions to process

# source
source("scripts/TUA_processing.R")
source("scripts/date_place_labeller.R")
source("scripts/quiz_processing.R")
source("scripts/question_weights.R")
source("scripts/cluster.R")
source("scripts/cluster_compacter.R")
source("scripts/canonicalizer.R")

# process TUA data 
processed_metadata_tua <- tua_processor(raw_metadata, raw_tua, raw_taskruns)

# date-label TUAs and IDs
labelled_metadata_tua <- label_date(processed_metadata_tua)

# process quiz answers
labelled_qs_ans <- quiz_processor(raw_qs_ans, labelled_metadata_tua)

# cluster, collapse, canonicalize
weights <- question_weighter(scheme_qs, labelled_qs_ans)

canonicalized_features <- canonicalizer(labelled_qs_ans)

### OUTPUT
write_csv(canonicalized_features, "data/canonicalized_features.csv")

