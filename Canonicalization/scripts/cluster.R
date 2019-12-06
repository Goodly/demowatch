#' Processes a table of question-answers from TagWorks for a given id, and
#' determines whether or not clustering is appropriate.
#'
#' @param tbl The input table of identifying information (task number,
#' contributor id, event id) and features
#' @param id The event id number for which cluster analysis will be performed
#' @param pg_cutoff The cutoff value for Pearson's Gamma. Describes the quality
#' required for a clustering to be accepted.

check_cluster <- function(tbl, weights, id, pg_cutoff = 0.9) {
  require(dplyr)
  require(cluster)
  require(fpc)
  
  # jaccard similarity helper function: returns coefficient used to measure the similarity between finite sets
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
  
  # filter input tbl for specific id and assign to id_tbl
  id_tbl <- tbl %>%
    filter(ids == id) %>%
    select(-c(task_pybossa_id, contributor_id, ids)) 
  
  # if there are two nodes (rows of id_tbl) and the jaccard similarity coefficient > 0.8, 
  # return input tbl filtered for specific id with cluster = 1
  # if there are two nodes and the JSC is not > 0.8, filter for id and return with cluster = [1,2]
  # else if there is one node, then just return the table with cluster = 1
  
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
  
  # compute Gower distance for dissimilarity (for use in agglomerative clustering)
  gower_dist <- id_tbl %>%
    daisy(metric = c("gower"), weights = weights$weights)
  
  # Plot clustering
  aggl_clust <- hclust(gower_dist, method = "complete")
  plot(aggl_clust)
  
  # Analysis of clustering; creates vector of distance-based statistics. If most recent
  # statistic > Pearson Gamma cutoff, then return the agglomerated table with cluster = number of clusters created
  # else if Pearson Gamma cutoff is never exceeded, return filtered table with cluster = 1
  pg <- c()
  for (i in 2:(num_nodes - 1)) {
    pg[i - 1] <-
      cluster.stats(gower_dist,
                    clustering = cutree(aggl_clust, k = i))["pearsongamma"][[1]]
    if (pg[i - 1] > pg_cutoff) { # Doesnt work for identical entries?
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
