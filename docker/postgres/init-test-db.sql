-- Runs once, on first initialisation of the postgres volume.
-- The test suite needs a database it can migrate and truncate freely, kept
-- separate from the development one so a test run never touches local data.
CREATE DATABASE le_bon_coin_test;
