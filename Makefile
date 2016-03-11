default: pip install -r requirements.txt

# Deletes DB, re-migrates, runs the gen_db script, and prompts the user to create a superuser 
db:
	rm db.sqlite3
	python fridgefiller/manage.py makemigrations
	python fridgefiller/manage.py migrate
	python fridgefiller/lists/generate_db.py
	python fridgefiller/manage.py createsuperuser
