### INPUT -> PROCESS -> OUTPUT PIPELINE ###
library(readr)

dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

### INPUT
### load raw data
raw_metadata <- read_csv("data/metadata_table.csv")
raw_tua <- read_csv("data/textthresher/DF_Crowd1.0_DataHunt-TUAS.csv")
raw_taskruns <- 




### PROCESS
### source and call functions to process

# source
source('scripts/TUA_processing.R')
source()

# process TUA data -> event IDs



### 