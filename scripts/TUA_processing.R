#' Takes in raw metadata and TUA texts from text thresher and processes them
#' into a clean tabular format. Meant to prep data for data-place labelling.
#' 
#' @param metadata_tbl A dataframe containing the metadata (place, 
#' publishing date, etc.)
#' @param tua_tbl A dataframe containing the TUA texts and keys for joining
#' to the metadata
#' @param taskrun_tbl A dataframe containing the raw taskruns
#' 
#' @import readr
#' @import dplyr

tua_processor <- function(metadata_tbl, tua_tbl, taskrun_tbl) {
  library(readr)
  library(dplyr)
  
  ### Group task runs by task ID and choose one, merge in publication date and location
  metadata <- taskrun_tbl %>% 
    group_by(task_id) %>%
    slice(1) %>% 
    inner_join(metadata_tbl, by = c("task_id" = "id")) %>%
    select(c("task_id", 
             "info_article_article_number",
             "info_article_text.x",
             "info_highlights_0_case_number",
             "info_article_metadata_city",
             "info_article_metadata_date_published"))
  
  ### Append TUA text to metadata table.
  metadata_with_tua <- tua_tbl %>% 
    inner_join(metadata, 
               by = c("article_number" = "info_article_article_number", 
                      "case_number" = "info_highlights_0_case_number")) %>%
    select(-c("topic_name")) %>%
    select(c(5, 1, 3, 7, 8, 4, 6, 2)) %>%
    rename(event_place = info_article_metadata_city,
           date_published = info_article_metadata_date_published,
           TUA = offsets)
  
  ### Function designed to clean TUA text, removing so-called trash characters.
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
  
  ### Apply above function to table to clean TUA text.
  metadata_with_tua$TUA <- sapply(metadata_with_tua$TUA, tua_parser)
  
  ### Return table containing metadata and clean TUA text, one row per task ID
  return(metadata_with_tua)
}
