# Data Producers for Smoothstack Scrumptious

* [Setup Python Virtual Environment](#setup-python-virtual-environment)
    * [UNIX](#unix)
    * [Windows](#windows)
* [Setup MySQL Database](#setup-mysql-database)
    * [Start up the Docker container](#start-up-the-docker-container)
    * [Check the connection](#check-the-connection)
    * [Verify setup](#verify-setup)
* [Run Producer Application](#run-producer-python-application)
    * [Test database connection](#test-database-connection)
    * [Run producers](#run-producers)
    * [Run tests](#run-tests)
* [Run in Production](#run-in-production)


## Setup Python Virtual Environment

### UNIX
```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt

# To deactivate the virtual env run
(.venv) $ deactivate
$
```

### Windows

```shell
C:\> python -m venv .venv
C:\> .\.venv\Scripts\activate.bat
(.venv) C:\> pip install -r requirements.txt

# To deactivate the virtual env run
(.venv) C:\> deactivate
C:\>
```

## Setup MySQL Database

### Start up the Docker container

MySQL database is run in a Docker container. You should have [Docker][docker] installed on your development machine.

```shell
$ docker-compose up
```

### Check the connection

A MySQL container should now be running. You can test that you can connect to it if you have the MySQL client configured

```
$ mysql -h 127.0.0.1 -u root
Welcome to the MySQL monitor.  Commands end with ; or \g.
...
mysql>
```

### Verify setup

Make sure the schema is set up correctly

```
mysql> use scrumptious;
Database changed
mysql> show tables;
+-----------------------+
| Tables_in_scrumptious |
+-----------------------+
| address               |
| category              |
| category_menuItem     |
| customer              |
| customer_address      |
| delivery              |
| driver                |
| menuItem              |
| menuItem_order        |
| menu_category         |
| order                 |
| orderPayment          |
| order_restaurant      |
| restaurant            |
| restaurant_category   |
| restaurant_owner      |
| tag                   |
| tag_menuItem          |
| user                  |
+-----------------------+
19 rows in set (0.00 sec)
```

>**NOTE:** With this `docker-compose` setup, persistent volumes will be setup to save data.
> The SQL init scripts will only be run one time. If you make any changes to the scripts
> and want them re-run, you will need to delete the volumes and run `docker-compose` up again.
> 
>     $ docker volume ls
>     local     ss-scrumptious-data-producers_mysql_config
>     local     ss-scrumptious-data-producers_mysql_data
>     $ docker volume rm ss-scrumptious-data-producers_mysql_config
>     $ docker volume rm ss-scrumptious-data-producers_mysql_data

### Shutdown MySQL Container

```shell
# CTRL-C out of the running container then run
$ docker-compose down
```


## Run Producer Python Application

### Test database connection

```shell
(.venv) $ python app/main.py
```

### Run producers

Example commands to run producer programs

#### User Producer

```shell
(.venv) $ python -m app.producers.users --help
(.venv) $ python -m app.producers.users --custs 10
(.venv) $ python -m app.producers.users --custs 10 --admins 2 --emps 5
(.venv) $ python -m app.producers.users --csv <path-to-csv-file>
```

#### Order Producer

To create new Orders, there needs to be customers and deliveries in the database.
If there are none, the [`testdata.py`](#order-dependency-data) program can be
used to create some dummy data.

```shell
(.venv) $ python -m app.produders.items --help
(.venv) $ python -m app.produders.items --count 10 --active 5
```

#### Order dependency data

To create dependency data for Orders, you can use the `testdata.py` program.

```shell
(.venv) $ python -m test.testdata --help
(.venv) $ python -m test.testdata --all 5
```

The last command will create 5 customers, addresses, deliveries, and drivers.
It will also create 10 users, 5, customer users and 5 driver users.

### Run tests

Make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
Make sure Java runtime is installed and `JAVA_HOME` environment variable is set up.
Test files should end with `_test.py`. Tests will be run using an H2 database.

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ test/runtests.sh
```

To use H2, the tests require two environment variables, `ENV_FILE` and `CLASSPATH`.

* `ENV_FILE` - the `.env` file used for environment variables.
* `CLASSPATH` - the Java classpath to find classes required for the JVM

The [`test/runtests.sh`](/test/runtests.sh) file sets these environment variables. If you are running
individual tests, instead of the entire test suite, you will need to set these

```shell
(.venv) $ ENV_FILE='./test/.env.test';CLASSPATH='./db/h2/lib/*' \
 pytest test/producers/users_test.py::test_user_arg_parser
```

Test files should end with `_test.py`. Tests will be run using an H2 database.

## Run in Production

* First make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
* Environment variables should be set up for:
    * `DATABASE_URL`
    * `DATABASE_USER`
    * `DATABASE_PASSWORD`

```shell
$ export DATABASE_USERNAME='<username>'
$ export DATABASE_PASSWORD='<password>'
$ export DATABASE_URL='jdbc:mysql://localhost:3306/scrumptious'
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ python -m app.producers.users --admins 5 --custs 5
```

[docker]: https://docs.docker.com/get-docker/