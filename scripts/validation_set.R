library(dplyr)
library(readr)

dir <- "~/df-canonicalization/"
setwd(dir)
reading_set <- read_csv("notebooks/reading_set.csv")

file_names <- list.files("data/city")
city_names <- gsub("\\+", " ", gsub(".csv", "", list.files("data/city")))

city_data_dir <- "data/city/"
hand_labels <- cbind(city = city_names[1], 
                     read_csv(paste0(city_data_dir, file_names[1])))
for (obj in 2:length(file_names)) {
  new_city <- cbind(city = city_names[obj], 
                    read_csv(paste0(city_data_dir, file_names[obj])) + 
                      max(hand_labels[, 2]))
  hand_labels <- rbind(hand_labels, new_city)
}
hand_labels <- hand_labels %>% mutate(city = as.character(city))

unique_cities <- unique(reading_set$city)
for (obj in 1:length(unique_cities)) {
  current_city <- unique_cities[obj]
  if (current_city %in% city_names) {
    next
  } else {
    hand_labels <- rbind(hand_labels, 
                         list(current_city, max(hand_labels$ID) + 1))
  }
}

labelled_tbl <- cbind(reading_set %>% filter(city == "Charleston"),
                      hand_labels %>%
                        filter(city == "Charleston") %>%
                        select(ID))
for (obj in 2:length(unique_cities)) {
  city_tbl <- reading_set %>% filter(city == unique_cities[obj]) 
  city_labels <- hand_labels %>% filter(city == unique_cities[obj])
  labelled_tbl <- rbind(labelled_tbl, cbind(city_tbl, ID = city_labels$ID))
}
labelled_tbl <- labelled_tbl %>% select(city, date, text, ID)
write_csv(labelled_tbl, "validation_set.csv")
