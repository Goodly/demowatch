library(testthat)
context("Testing date-place labeller")

library(readr)
dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

source("scripts/date_place_labeller.R")

if (FALSE) {
  source("scripts/pipeline.R")
  test_that("date labelling works", {
    actual_date_labelled_data <- labelled_metadata_tua
    expected_date_labelled_data <- readRDS(file="tests/data/labelled_metadata_tua.rds")
    expect_equal(actual_date_labelled_data, expected_date_labelled_data)
  })
}

test_that("date labelling works for simple toy data set", {
  input_data <- readRDS(file="tests/data/dl_input1.rds")
  actual_date_labelled_data <- label_date(input_data)
  expected_date_labelled_data <- readRDS(file="tests/data/dl_output1.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

test_that("date labelling phase 1 works", {
  input_data <- readRDS(file="tests/data/dl_input2.rds")
  actual_date_labelled_data <- label_date(input_data)
  expected_date_labelled_data <- readRDS(file="tests/data/dl_output2.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

test_that("date labelling phase 2 works", {
  input_data <- readRDS(file="tests/data/dl_input3.rds")
  actual_date_labelled_data <- label_date(input_data)
  expected_date_labelled_data <- readRDS(file="tests/data/dl_output3.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

test_that("date labelling phase 3 works", {
  input_data <- readRDS(file="tests/data/dl_input4.rds")
  actual_date_labelled_data <- label_date(input_data)
  expected_date_labelled_data <- readRDS(file="tests/data/dl_output4.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

test_that("date labelling works with null values", {
  input_data <- readRDS(file="tests/data/dl_input5.rds")
  actual_date_labelled_data <- label_date(input_data)
  expected_date_labelled_data <- readRDS(file="tests/data/dl_output5.rds")
  expect_equal(actual_date_labelled_data, expected_date_labelled_data)
})

# input_data <- readRDS(file="tests/data/dl_input5.rds")
# output <- label_date(input_data)
# saveRDS(output, file = "tests/data/dl_output5.rds")
