library(testthat)
context("Testing final canonicalizations")

source("scripts/pipeline.R")

test_that("final canonicalization is correct", {
  actual_canonicalized_data <- canonicalized_features
  expected_canonicalized_data <- read_csv("tests/data/canonicalized_features_reference.csv")
  expect_equal(actual_canonicalized_data, expected_canonicalized_data)
})