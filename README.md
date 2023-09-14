# Backend

### How to use :

Follow the recipe  
1. Settings and database
    1. build psycity/psycity/local_settings.py \
    2. put the code bellow in that file
    ```
    from .settings import *

    DEBUG = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME' : 'db.sqlite3'
        }
    }

    ```
2. Set the environment variables:  
    in linux you can set env like below  
    ```export DJANGO_SETTINGS_MODULE=psycity.local_settings```
2. Install requirements: \
    install the god damn requirements no matter how  
    you can use venv or no just install them simply.  
    ```
    $ python -m venv venv
    $ source venv/bin/activate      #in linux
    $ pip install -r requirements.txt
    ```
3. Migrations:
    1. `python manage.py makemigrations`
    2. `python manage.py migrate`

4. Runserver:  
    `python manage.py runserver`


then check out schema in `127.0.0.1:8000/swagger/` or `127.0.0.1:8000/redoc/`