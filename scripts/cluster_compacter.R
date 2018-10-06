### Call Sidney's Helper Function, which returns 3-column table (Task ID, Contributor ID, Cluster ID)
# Grab clusters, apply any function, concatenate rows
cluster_compacter <- function(cluster_tbl, labelled_qs_ans, id) {
  ### helper function for compacting
  compact <- function(df, cluster_num) {
    new_df <- df[1, ]
    new_df[1, 1] <- max(df[, 1])
    for (i in 3:ncol(df)) {
      new_df[1, i] <- max(df[, i])
    }
    new_df <- cbind(task_pybossa_id = new_df[1, 1], 
              cbind(new_df[1, 3:ncol(df)],
                    cluster = c(cluster_num)))
    return(new_df)
  }
  
  ### filter out feature input for specific ID
  id_and_features <- labelled_qs_ans %>% filter(ids == id)
  
  size <- max(cluster_tbl$cluster)
  if (size == 1) {
    return(id_and_features %>%
             select(-c(contributor_id)) %>% 
             mutate(cluster = 1) %>% slice(1)) # task_pybossa_id, 
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

# id = 3
# cluster_tbl <- check_cluster(labelled_qs_ans, id, 0.9)
# print(id)
# compact_cluster <- cluster_compacter(cluster_tbl, labelled_qs_ans, id) %>%
# mutate(ids = max(canonicalized_features$ids) + cluster)
# canonicalized_features <- rbind(canonicalized_features, compact_cluster)

# canonicalized_features <- data.frame()
# for (id in unique(labelled_qs_ans$ids)) {
#   cluster_tbl <- check_cluster(labelled_qs_ans, id, 0.9)
#   print(id)
#   if (sum(dim(canonicalized_features)) == 0) {
#     compact_cluster <- cluster_compacter(cluster_tbl, labelled_qs_ans, id) %>%
#       mutate(ids = cluster)
#     canonicalized_features <- compact_cluster
#   } else {
#     compact_cluster <- cluster_compacter(cluster_tbl, labelled_qs_ans, id) %>%
#       mutate(ids = max(canonicalized_features$ids) + cluster)
#     canonicalized_features <- rbind(canonicalized_features,
#                                     compact_cluster)
#   }
# }
# canonicalized_features <- canonicalized_features %>% select(-cluster)
