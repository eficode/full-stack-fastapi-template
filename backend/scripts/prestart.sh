#! /usr/bin/env bash

set -e
set -x

# Let DynamoDB start and check the connection
python app/backend_pre_start.py

# Create initial data in DB (tables and superuser)
python app/initial_data.py
