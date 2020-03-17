#!/usr/bin/python3
import os

# in Dockerfile we set the WORKDIR to /ch_api.
# If you don't run in Docker make sure your working (root) directory is ch_api/
cwd = os.getcwd()

# absolute path to the file holding the api key.
API_KEY_ABS_PATH = cwd + "/utils/api_key"
# print(API_KEY_ABS_PATH)
