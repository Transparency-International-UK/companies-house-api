#!/usr/bin/python3
import os

# in Dockerfile we set the WORKDIR to /ch_api.
# If you don't run in Docker make sure your working (root) directory is ch_api/
cwd = os.getcwd()

# absolute path to the database config file
DB_CONFIG_ABS_PATH = cwd + "/db/database.ini"
# print(DB_CONFIG_ABS_PATH)

# section in the database config file with params to connect locally.
DB_CONFIG_SECTION = "PostgreSQL"

# name of the schema to be created/connected to.
DB_SCHEMA = "app_test"
