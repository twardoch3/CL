# Cinema-App
Application allows to manage database in cinema (add, edit or delete movies, cinemas, tickets, payments).

### Requirements
Program requires PostgreSQL database and Python Flask.

### Installing
Install requirements  with command :
```
pip install -r requirements.txt
```

### Running the program
Connection info (homework_day2_fn_cl.py):
```
class DB:
    username = "postgres"
    passwd = "coderslab"
    hostname = "localhost"
    db_name = "homework_d2" 
```
Start a development Web server on the local machine with command:
```
python3 homework_day2_flask.py
```
Create database clicking on button 'Create/Clean DB'.



### Usage Examples:
Add movie:
```
http://127.0.0.1:5000/new/movies
```
Manage tickets:
```
http://127.0.0.1:5000/modify?tabela=tickets
```
Manage payments:
```
http://127.0.0.1:5000/payments_details
```
