#!/bin/bash

SCHEMA_PATH="./share/user_schema.sql"
ENV_FILE=".env"

# Check if ENV_FILE exists
if [ ! -f $ENV_FILE ]; then
	echo "\e[31mError: .env File Not Found\e[0m"
	echo "To create .env file, run this command:"
	echo '   "sh ./bin/create-dotenv.sh"'
	exit 1
fi

# Load ENV_FILE
export $(grep -v '^#' $ENV_FILE | xargs)

if [ -f $USER_SERVICE_PRIMARY_DB_PATH ]; then
	echo "Error: User database already exists."
	exit 1
fi

if [ ! -f $SCHEMA_PATH ]; then
	echo "Error - File Not Found: ${SCHEMA_PATH}"
	exit 1
fi

mkdir -p "$(dirname $USER_SERVICE_PRIMARY_DB_PATH)"
sqlite3 $USER_SERVICE_PRIMARY_DB_PATH < $SCHEMA_PATH

if test -f $USER_SERVICE_PRIMARY_DB_PATH; then
	echo "User database has been created."
fi