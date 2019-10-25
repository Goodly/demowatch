library(testthat)
context("Testing date-place labeller")

source ("scripts/pipeline.R")

test_that("date labelling works", {
  actual_date_labelled_data <- labelled_metadata_tua
  expected_date_labelled_data <- readRDS(file="tests/data/labelled_metadata_tua.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

test_that("date labelling works for toy data set", {
  actual_date_labelled_data <- label_date()
  # TODO....
})