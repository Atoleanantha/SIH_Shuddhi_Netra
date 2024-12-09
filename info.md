- pip install virtualenv
- python -m venv env
- activate env- env/Scripts/activate   

- pip install -r requirements.txt


- deactivate
- pip install django
- django-admin startproject backend_api
- python manage.py startapp users
- python manage.py runserver

- install postgresql and pgadmin

- pip install psycopg2-binary

- pip install djangorestframework

- python manage.py startapp Auth

- username= atole
- email= atoleanantha03@gmail.com
- 123456

git remote add origin https://github.com/Atoleanantha/SIH_Shuddhi_Netra.git
git branch -M main
git push -u origin main

 git branch phase2-events  //new branch

 git checkout phase2-events //switch branch

 git push -u origin phase2-events //push new brach to github
 git push -u origin phase3-events //push new brach to github

 -celery -A backend beat -l INFO



t=5432 dbname=postgres user=postgres sslmode=prefer connect_time
out=10" 2>>&1
psql (16.6)
WARNING: Console code page (437) differs from Windows code page
(1252)
         8-bit characters might not work correctly. See psql ref
erence
         page "Notes for Windows users" for details.
Type "help" for help.

postgres=# CREATE DATABASE Shuddhinetra
postgres-# CREATE USER shuddhinetra WITH PASSWORD 123456
postgres-# ;
ERROR:  syntax error at or near "CREATE"
LINE 2: CREATE USER shuddhinetra WITH PASSWORD 123456
        ^
postgres=# CREATE DATABASE Shuddhinetra;
CREATE DATABASE
postgres=# CREATE USER shuddhinetra WITH PASSWORD 123456;
ERROR:  syntax error at or near "123456"
LINE 1: CREATE USER shuddhinetra WITH PASSWORD 123456;
                                               ^
postgres=# CREATE USER shuddhinetra WITH PASSWORD "123456";
ERROR:  syntax error at or near ""123456""
LINE 1: CREATE USER shuddhinetra WITH PASSWORD "123456";
                                               ^
postgres=# CREATE USER shuddhinetra WITH PASSWORD '123456';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE Shuddhinetra TO shud
dhinetra;
GRANT
postgres=#




























twilio recovery code-
- 2DEXMZ8BTT3RXPZNGYWZMF12

narendra
- X26CZS3JSBRVCUC1KS84TGHK
<!-- 
account_sid = 'ACcd924dd4d8aaaee27998cb4d2e739617'
auth_token = '90e304e966efbff03bda6f9c3aedd907'
client = Client(account_sid, auth_token)
message = client.messages.create(
  from='+17752958692',
  body='hello nerendra',
  to='+18777804236'
) -->