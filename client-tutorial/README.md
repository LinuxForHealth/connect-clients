# LinuxForHealth client-tutorial

The client-tutorial project demonstrates the enrichment of EMR patient data using IBM Watson Health Annotator for Clinical Data and LinuxForHealth.

## Required Software
- [git](https://git-scm.com) for project version control
- [Python 3.8 or higher](https://www.python.org/downloads/mac-osx/) for runtime/coding support
- [Pipenv](https://pipenv.pypa.io) for Python dependency management  
- [Docker Compose 1.28.6 or higher](https://docs.docker.com/compose/install/) for a local container runtime
- [MySQL client](https://dev.mysql.com/downloads/shell) for patient data storage

## Installation
1. Clone the LinuxForHealth connect and connect-clients repositories:
```shell
git clone https://github.com/LinuxForHealth/connect.git
git clone https://github.com/LinuxForHealth/connect-clients.git
```

2. Set up the client-tutorial virtual environment
```shell
cd connect-clients/client-tutorial
pip install --upgrade pip
pipenv sync --dev
```

3. Set up the connect virtual environment
```shell
cd ../../connect
pipenv sync --dev
```

4. Add the mysql service
Add the mysql service from the client-tutorial docker-compose file (client-tutorial/client_tutorial/docker-compose.yml) to the bottom of the connect docker-compose file (connect/docker-compose.yml).
```shell
  mysql:
    profiles: ["deployment"]
    image: mysql:8.0.15
    ports:
        - "3306:3306"
    volumes:
       - ./database-scripts:/docker-entrypoint-initdb.d
    environment:
        MYSQL_ROOT_USER: root
        MYSQL_ROOT_PASSWORD: secret
        MYSQL_DATABASE: kafkaFhirDemoDb
        MYSQL_USER: lfhuser
        MYSQL_PASSWORD: changePassword
```

5. Start the LinuxForHealth connect and client-tutorial services:
In the connect directory:
```shell
docker-compose --profile deployment up -d
```

6. Populate the MySQL server with sample data:
```shell
cd ../connect-clients/client-tutorial/client_tutorial/database-scripts
mysql -h localhost -P 3306 --protocol=tcp -u root -p kafkaFhirDemoDb < 001-create-db.sql
```
enter the default password "secret" when prompted.

## Run
Run the tutorial service
```shell
pipenv run tutorial
```
Run the tutorial application
```shell
pipenv run flask
```
Run the tests
```shell
pipenv run tests
pipenv run nlptest
```

## Resources
[client-tutorial details](./client_tutorial/README.md)
