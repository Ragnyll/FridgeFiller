default: 
	pip install -r requirements.txt

run: 
	python fridgefiller/manage.py runserver

# Deletes DB, re-migrates, runs the gen_db script, and prompts the user to create a superuser 
db: migrations 
	rm -f db.sqlite3
	python fridgefiller/manage.py makemigrations
	python fridgefiller/manage.py migrate
	python fridgefiller/lists/generate_db.py
	python fridgefiller/manage.py createsuperuser

migrations: fridgefiller/lists/migrations
	rm -rf $<
	mkdir -p $<
	touch $</__init__.py
