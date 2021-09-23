#!/bin/bash

export CLASSPATH='./db/h2/lib/*'
export ENV_FILE='./test/.env.test'


rm ./tmp/data/db.mv.db 2> /dev/null
rm ./tmp/data/db.trace.db 2> /dev/null
java -jar db/h2/h2-mysql-functions.jar jdbc:h2:./tmp/data/db
python -m test.init_db
pytest ./test
