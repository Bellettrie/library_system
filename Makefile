buildstatic:
	cd jstoolchain && npx tailwindcss -c tailwind.config.js -o ../static/css/main.css
	python manage.py collectstatic
