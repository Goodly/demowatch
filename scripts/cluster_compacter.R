### Call Sidney's Helper Function, which returns 3-column table (Task ID, Contributor ID, Cluster ID)
# Grab clusters, apply any function, concatenate rows
cluster_compacter <- function(cluster_tbl, labelled_qs_ans, id) {
  ### helper function for compacting
  compact <- function(df, cluster_num) {
    new_df <- df[1, ]
    for (i in 3:ncol(df)) {
      new_df[1, i] <- max(df[, i])
    }
    new_df <- cbind(new_df[1, 3:ncol(df)],
                    cluster = c(cluster_num))
    return(new_df)
  }
  
  ### filter out feature input for specific ID
  id_and_features <- labelled_qs_ans %>% filter(ids == id)
  
  size <- max(cluster_tbl$cluster)
  if (size == 1) {
    return(id_and_features %>%
             select(-c(task_pybossa_id, contributor_id)) %>%
             mutate(cluster = 1) %>% slice(1))
  }
  
  dataframe_list <- vector("list", size)
  for (i in 1:nrow(cluster_tbl)) {
    dataframe_list[[cluster_tbl[i, 3]]] <-
      rbind(dataframe_list[[cluster_tbl[i, 3]]], id_and_features[i,])
  }
  
  for (i in 1:size) {
    dataframe_list[[i]] <- compact(dataframe_list[[i]], i)
  }
  
  clusters_and_features <- dataframe_list[[1]]
  for (i in 2:size) {
    clusters_and_features <-
      rbind(clusters_and_features, dataframe_list[[i]])
  }
  
  return(clusters_and_features)
}
