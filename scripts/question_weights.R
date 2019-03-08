#' Reads and converts the additive/contradictory nature of the question scheme
#' into numeric weights
#' 
#' @param scheme_tbl A dataframe of the question scheme tagged with additive/
#' contradictory.
#' 
#' @import dplyr

question_weighter <- function(scheme_tbl, labelled_qs_ans) {
  library(dplyr)
  
  ### calculate question weights
  weights <- scheme_tbl
  weights[, 2][weights[, 2] == "Additive"] <- 0.1
  weights[, 2][weights[, 2] == "Ambiguous"] <- 0.5
  weights[, 2][weights[, 2] == "Contradictory"] <- 1
  weights <- weights %>% 
    mutate(weights = as.numeric(Type), q_name = as.character(Number)) %>% 
    select(5, 4)
  
  for (i in 1:length(weights$q_name)) {
    if (nchar(weights$q_name[i]) != 4) {
      weights$q_name[i] <- paste0(weights$q_name[[i]], "0")
    }
  }
  
  q_ans_combos <- data.frame(col = colnames(labelled_qs_ans[, -c(1, 2, 297)]))
  q_ans_combos$q_name <- substr(q_ans_combos$col, 0, 4)
  
  weights <- weights %>% right_join(q_ans_combos, by = c("q_name"))
  weights$weights[is.na(weights$weights)] <- 0
  return(weights)  
}
