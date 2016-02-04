# Getting Set Up & Developing

First, make sure you're using a UNIX environment.  Windows works, but our project probably won't support it.

1.  Install [pip](https://pypi.python.org/pypi/pip)

2.  Install project dependencies via `$ pip install -r requirements.txt` from the project root.

3.  Migrate the database with `$ python cs4096/manage.py migrate`

4.  Run the Django server via `$ python manage.py runserver`.  This will start the Django debug server, running at `localhost:8000` on your machine.  If you want to access the app from your public ip (aka from another computer on the network), instead run the Django server with `$ python manage.py runserver 0.0.0.0:<port number>`

5.  Have fun!