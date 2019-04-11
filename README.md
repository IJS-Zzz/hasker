# Hasker: Poor Man's Stackoverflow
Homework for Otus course - [otus.ru](https://otus.ru/lessons/razrabotchik-python/)
Q&A analog of stackoverflow on Django 2.0

### Author
Игорь Смуров
email: smurov_igor@mail.ru

### Requirements
* Python 3
* Django 2.0
* PostgreSQL

##### Python packages:
* django-debug-toolbar (on development)
* psycopg2
* uwsgi

### Run Docker container
```
docker run --rm -it -p 8080:80 ubuntu /bin/bash
```

### Prepare
```
apt-get update
apt-get upgrade -y
apt-get install -y git \
                   make
git clone https://github.com/IJS-Zzz/hasker.git
```

### Build
```
cd hasker
make prod
```