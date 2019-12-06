library(testthat)
context("Testing final canonicalizations")

library(readr)
dir <- readline("Enter the directory for the `df-canonicalization` folder (without quotes):")
setwd(dir)

source("scripts/canonicalizer.R")

if (FALSE) {
  source("scripts/pipeline.R")
  test_that("final canonicalization is correct", {
    actual_canonicalized_data <- canonicalized_features
    expected_canonicalized_data <- readRDS(file="tests/data/canonicalized_features_reference.rds")
    expect_equal(actual_canonicalized_data, expected_canonicalized_data)
  })
}

test_that("canonicalizer works for simple toy data set", {
  input_data <- readRDS(file="tests/data/dl_input6.rds")
  input_weights <- readRDS(file="tests/data/dl_weights6.rds")
  actual_canonicalized_data <- canonicalizer(input_data, input_weights)
  expected_canonicalized_data <- readRDS(file="tests/data/dl_output6.rds")
  expect_equal(actual_canonicalized_data, expected_canonicalized_data)
})

test_that("check_cluster works for larger toy data set", {
  input_data <- readRDS(file="tests/data/dl_input7.rds")
  input_weights <- readRDS(file="tests/data/dl_weights6.rds")
  actual_clustered_data <- check_cluster(input_data, input_weights, 1, 0.8)
  expected_clustered_data <- readRDS(file="tests/data/dl_output7.rds")
  expect_equal(actual_clustered_data, expected_clustered_data)
})

test_that("cluster_compacter works for larger toy data set", {
  input_data <- readRDS(file="tests/data/dl_input7.rds")
  input_cluster <- readRDS(file="tests/data/dl_output7.rds")
  actual_compacted_data <- cluster_compacter(input_cluster, input_data, 1)
  expected_compacted_data <- readRDS(file="tests/data/dl_output8.rds")
  expect_equal(actual_compacted_data, expected_compacted_data)
})

# input_data <- readRDS(file="tests/data/dl_input7.rds")
# input_cluster <- readRDS(file="tests/data/dl_output7.rds")
# output <- cluster_compacter(input_cluster, input_data, 1)
# saveRDS(output, file = "tests/data/dl_output8.rds")