rm db.sqlite3
python manage.py migrate
python manage.py load_authors_from_db
python manage.py load_works_from_db

python manage.py load_authors_matched_to_works
python manage.py load_series_titles
python manage.py load_members_from_db
python manage.py pseudonymise
python manage.py load_lendings_from_db
python manage.py load_categories
python manage.py add_committees