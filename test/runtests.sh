#!/bin/bash

export ENV_FILE='./test/.env.test'
export CLASSPATH='./db/h2/lib/*'

java -jar db/h2/h2-mysql-functions.jar jdbc:h2:./tmp/data/db
python -m test.init_db
pytest
