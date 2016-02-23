# Getting Set Up & Developing

First, make sure you're using a UNIX environment.  Windows works, but our project probably won't support it.

1.  Install [pip](https://pypi.python.org/pypi/pip)

2.  Install project dependencies via `$ pip install -r requirements.txt` from the project root.

3.  Create migrations for the lists app `$ python fridgefiller/manage.py makemigrations lists`

4.  Migrate the database with `$ python fridgefiller/manage.py migrate`

5. Add data to the database. Run `$ python lists/generate.py` to generate a database with some models n' what not.
   Do note that running this command expects an empty database, if the database is not empty there might be problems

6.  Run the Django server via `$ python manage.py runserver`.  This will start the Django debug server, running at `localhost:8000` on your machine.  If you want to access the app from your public ip (aka from another computer on the network), instead run the Django server with `$ python manage.py runserver 0.0.0.0:<port number>`

7.  Have fun!