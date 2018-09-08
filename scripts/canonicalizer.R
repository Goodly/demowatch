#' Canonicalization -- for given question weights and answers given by 
#' readers, representation for events identified by other means. 
#' 
#' @param labelled_qs_ans a dataframe with the questions-answers for 
#' each task run, and columns with unique event IDs
#' 
#' @param pg Pearson's gamma for clustering. Describes the minimum 
#' "quality" of clustering needed for a clustering to be accepted.

canonicalizer <- function(labelled_qs_ans, pg = 0.9) {
  canonicalized_features <- data.frame()
  
  for (id in unique(labelled_qs_ans$ids)) {
    cluster_tbl <- check_cluster(labelled_qs_ans, id, pg)
    print(id)
    if (sum(dim(canonicalized_features)) == 0) {
      compact_cluster <- cluster_compacter(cluster_tbl, labelled_qs_ans, id) %>%
        mutate(ids = cluster)
      canonicalized_features <- compact_cluster
    } else {
      compact_cluster <- cluster_compacter(cluster_tbl, labelled_qs_ans, id) %>%
        mutate(ids = max(canonicalized_features$ids) + cluster)
      canonicalized_features <- rbind(canonicalized_features, 
                                      compact_cluster)
    }
  }
  
  canonicalized_features <- canonicalized_features %>% select(-cluster)
  return(canonicalized_features)
}