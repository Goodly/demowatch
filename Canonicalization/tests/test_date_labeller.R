library(testthat)
context("Testing date-place labeller")

# source("scripts/pipeline.R")
source("scripts/date_place_labeller.R")
setwd("~/Documents/BerkeleySem6/demowatch/Canonicalization")

# test_that("date labelling works", {
  # actual_date_labelled_data <- labelled_metadata_tua
  # expected_date_labelled_data <- readRDS(file="tests/data/labelled_metadata_tua.rds")
  # expect_equal(actual_date_labelled_data, expected_date_labelled_data)
# })

test_that("date labelling works for simple toy data set", {
  input_data <- readRDS(file="tests/data/date_labelling_input_data.rds")
  actual_date_labelled_data <- label_date(input_data)
  expected_date_labelled_data <- readRDS(file="tests/data/date_labelling_output.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

# test phases 1, 2, 3