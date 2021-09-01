# Data Producers for Smoothstack Scrumptious

* [Setup Python Virtual Environment](#setup-python-virtual-environment)
    * [UNIX](#unix)
    * [Windows](#windows)
* [Setup MySQL Database](#setup-mysql-database)
    * [Start up the Docker container](#start-up-the-docker-container)
    * [Check the connection](#check-the-connection)
    * [Verify setup](#verify-setup)
* [Run Producer Application](#run-producer-python-application)


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
(.venv) C:\> pip install -r requirements

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

```shell
$ python app/main.py
```


[docker]: https://docs.docker.com/get-docker/