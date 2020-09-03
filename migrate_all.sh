rm db.sqlite3
python3 manage.py migrate
python3 manage.py load_works_from_db 2
python3 manage.py load_authors_from_db
python3 manage.py load_authors_matched_to_works
python3 manage.py load_series_titles
python3 manage.py load_members_from_db
python3 manage.py load_lendings_from_db
python3 manage.py load_categories
python3 manage.py add_committees
python3 manage.py set_author_sort_text
python3 manage.py read_committee_csv
python3 manage.py load_book_codes
python3 manage.py set_author_identifying_codes
python3 manage.py load_comments
python3 manage.py load_ratings
python3 manage.py load_recodings
python3 manage.py set_year_publication
python3 manage.py add_member_types
python3 manage.py load_member_types_from_db