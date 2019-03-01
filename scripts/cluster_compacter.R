### Call Sidney's Helper Function, which returns 3-column table (Task ID, Contributor ID, Cluster ID)
# Grab clusters, apply any function, concatenate rows
cluster_compacter <- function(cluster_tbl, labelled_qs_ans, id) {
  
  ### filter out feature input for specific ID
  id_and_features <- labelled_qs_ans %>% filter(ids == id)
  clusters = unique(cluster_tbl$cluster)
  
  ### if there is only one cluster, compact and return
  size <- max(clusters)
  if (size == 1) {
    TUAs = paste(id_and_features$task_pybossa_id, id_and_features$contributor_id, sep = ': ', collapse = ' // ')
    clusters_and_features = id_and_features %>% 
      summarise_all(max) %>%
      select(-c('task_pybossa_id', 'contributor_id')) %>%
      mutate(TUA = TUAs, cluster = 1)
    # treat all as additive data since clustering decided things were not different "enough"
  } else {
    clusters_and_features = NA
    for (cluster_num in clusters) {
      
      # identifier for row of `id_and_features` -- to be changed
      cluster_rows = cluster_tbl %>% filter(cluster == cluster_num)
      task_id = cluster_rows$task_pybossa_id
      cont_id = cluster_rows$contributor_id
      
      TUAs = paste(task_id, cont_id, sep = ': ', collapse = ' // ') # change TUA info to something meaningful when IAA comes thru
      
      cluster_feats = id_and_features %>%
        filter((task_pybossa_id %in% task_id) & (contributor_id %in% cont_id)) %>%
        summarise_all(max) %>%
        select(-c('task_pybossa_id', 'contributor_id')) %>% 
        mutate(TUA = TUAs, cluster = cluster_num) 
      
      if (is.na(clusters_and_features)) {
        clusters_and_features = cluster_feats
      } else {
        clusters_and_features = rbind(clusters_and_features, cluster_feats)
      }
    }
  }
  return(clusters_and_features)
}
