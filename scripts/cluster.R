#' Processes a table of question-answers from TextThresher for a given id, and
#' determines whether or not clustering is appropriate.
#'
#' @param tbl The input table of identifying information (task number,
#' contributor id, event id) and features
#' @param id The event id number for which cluster analysis will be performed
#' @param pg_cutoff The cutoff value for Pearson's Gamma. Describes the quality
#' required for a clustering to be accepted.

check_cluster <- function(tbl, id, pg_cutoff = 0.9) {
  require(dplyr)
  require(cluster)
  require(fpc)
  
  # jaccard similarity helper function
  jaccard <- function(df, margin) {
    if (margin == 1 | margin == 2) {
      M_00 <- apply(df, margin, sum) == 0
      M_11 <- apply(df, margin, sum) == 2
      if (margin == 1) {
        df <- df[!M_00, ]
        j_sim <- sum(M_11) / nrow(df)
      } else {
        df <- df[, !M_00]
        j_sim <- sum(M_11) / length(df)
      }
      return(j_sim)
    } else break
  }
  
  # weights will be defined outside and are constant regardless of what rows 
  # are input
  id_tbl <- tbl %>%
    filter(ids == id) %>%
    select(-c(task_pybossa_id, contributor_id, ids)) 
  
  num_nodes <- nrow(id_tbl)
  
  if (num_nodes == 2) {
    if (jaccard(id_tbl, 2) > 0.8) {
      return(tbl %>% 
               filter(ids == id) %>%
               select(c(task_pybossa_id, contributor_id)) %>%
               mutate(cluster = 1))
    } else {
      return(tbl %>%
               filter(ids == id) %>%
               select(c(task_pybossa_id, contributor_id)) %>%
               mutate(cluster = c(1, 2)))
    }
  } else if (num_nodes == 1) {
    return(tbl %>% 
             select(c(task_pybossa_id, contributor_id)) %>%
             mutate(cluster = 1))
  }
  
  # dissimilarity
  gower_dist <- id_tbl %>%
    daisy(metric = c("gower"), weights = weights$weights)
  
  # clustering
  aggl_clust <- hclust(gower_dist, method = "complete")
  plot(aggl_clust)
  
  # analysis
  pg <- c()
  for (i in 2:(num_nodes - 1)) {
    pg[i - 1] <-
      cluster.stats(gower_dist,
                    clustering = cutree(aggl_clust, k = i))["pearsongamma"][[1]]
    if (pg[i - 1] > pg_cutoff) {
      return(tbl %>%
               filter(ids == id) %>%
               select(c(task_pybossa_id, contributor_id)) %>%
               mutate(cluster = cutree(aggl_clust, k = i)))
    }
  }
  return(tbl %>%
           filter(ids == id) %>%
           select(c(task_pybossa_id, contributor_id)) %>%
           mutate(cluster = 1))
}
