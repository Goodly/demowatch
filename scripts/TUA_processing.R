#' Takes in raw metadata and TUA texts from text thresher and processes them
#' into a clean tabular format. Meant to prep data for data-place labelling.
#' 
#' @param metadata_tbl A dataframe containing the metadata (place, 
#' publishing date, etc.)
#' @param tua_tbl A dataframe containing the TUA texts and keys for joining
#' to the metadata
#' 
#' @import readr
#' @import dplyr

tua_processor <- function(metadata_tbl, tua_tbl) {
  library(readr)
  library(dplyr)
  
  ###
  metadata_with_tua <- tua_tbl %>% 
    inner_join(metadata_tbl, 
               by = c("article_number" = "info_article_article_number", 
                      "case_number" = "info_highlights_0_case_number")) %>%
    select(-c("topic_name")) %>%
    select(c(5, 1, 3, 7, 8, 4, 6, 2)) %>%
    rename(event_place = info_article_metadata_city,
           date_published = info_article_metadata_date_published,
           TUA = offsets)
  
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
  metadata_with_tua$TUA <- sapply(metadata_with_tua$TUA, tua_parser)
  return(metadata_with_tua)
}
