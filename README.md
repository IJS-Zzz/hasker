# Hasker: Poor Man's Stackoverflow
Homework for Otus course - [otus.ru](https://otus.ru/lessons/razrabotchik-python/)<br>
Q&A analog of stackoverflow on Django 2.0

### Author
Игорь Смуров<br>
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

### Build (deploy)
```
cd hasker
make prod
```
---

### Configuration options
The project has config files for different run cases:

#### Development server
use dev.py config file (path: hasker/config/settings/dev.py) <br>
with dev.txt requirements (path: requirements/dev.txt)

###### run example
```
pip install -U -r requirements/dev.txt 
export DJANGO_SETTINGS_MODULE=hasker.config.settings.dev
python manage.py runserver
```

#### Production server
(used in deploy)
use prod.py config file (path: hasker/config/settings/prod.py) <br>
with prod.txt requirements (path: requirements/prod.txt)

note: you should run postgresql server with before run project

###### run example
```
pip install -U -r requirements/prod.txt 
export DJANGO_SETTINGS_MODULE=hasker.config.settings.prod
python manage.py runserver
```

### Testing
Run project tests:
```
python manage.py test
```