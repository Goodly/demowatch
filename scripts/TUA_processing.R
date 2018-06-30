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
write_csv(metadata_dat, "metadata_table.csv")