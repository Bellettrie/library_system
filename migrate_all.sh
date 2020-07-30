rm db.sqlite3
python3 manage.py migrate
python3 manage.py load_authors_from_db
python3 manage.py load_works_from_db 2

python3 manage.py load_authors_matched_to_works
python3 manage.py load_series_titles
python3 manage.py load_members_from_db
python3 manage.py load_lendings_from_db
python3 manage.py load_categories
python3 manage.py add_committees
