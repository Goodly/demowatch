weights <- read.csv('scheme_q_weights.csv')

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
  # weights will be defined outside and are constant regardless of what rows 
  # are input
  
  # dissimilarity
  gower_dist <- tbl %>%
    filter(ids == id) %>%
    select(-c(task_pybossa_id, contributor_id, ids)) %>%
    daisy(metric = c("gower"), weights = weights$weights)
  
  # clustering
  aggl_clust <- hclust(gower_dist, method = "complete")
  
  # analysis
  pg <- c()
  for (i in 2:6) {
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