library(readr)
library(dplyr)

###
dir <- "~/df-canonicalization/"
setwd(dir)

###
tua_dat <- read_csv("data/textthresher/DF_Crowd1.0_DataHunt-TUAS.csv")
metadata_dat <- read_csv("data/metadata_table.csv")

metadata_with_tua <- tua_dat %>% 
  inner_join(metadata_dat, 
             by = c("article_number" = "info_article_article_number", 
                    "case_number" = "info_highlights_0_case_number")) %>%
  select(-c("topic_name")) %>%
  select(c(5, 1, 3, 7, 8, 4, 6, 2)) %>%
  rename(event_place = info_article_metadata_city,
         date_published = info_article_metadata_date_published,
         TUA = offsets, 
         article_text = info_article_text.x)

###
tua_parser <- function(tua_text) {
  # trash characters to remove
  garbage <- c("”", "“")
  
  # split input into list of strings
  split_tua <- unlist(strsplit(tua_text, '\"'))
  
  # check and remove trash characters
  garbage_check <- sapply(garbage, grepl, split_tua)
  for (j in 1:ncol(garbage_check)) {
    for (i in 1:nrow(garbage_check)) {
      if (garbage_check[i, j]) {
        split_tua[i] <- gsub(garbage[j], "", split_tua[i])
      }}}
  without_extra <- split_tua[seq(2, length(split_tua), 2)]
  return(list(without_extra))
}


###
metadata_with_tua$TUA <- sapply(metadata_with_tua$TUA, tua_parser)


saveRDS(metadata_with_tua, "data/metadata_table.rds")

