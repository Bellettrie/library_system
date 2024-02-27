# Bellettrie System

This project (BS) contains the website / Library Management System of Bellettrie. BS uses Django as a web framework, and bootstrap for constructing pages. Other than that, it is light on dependencies, to lower the amount of dependency update hell.

## Setup of development environment
1. Download project from Git.
2. Install recent python version (3.10 or higher)
3. run pip install -r requirements.txt in the root of the project. You may want to look into virtual environments.
4. Install docker-desktop (or docker + docker-compose).
5. Start up docker-desktop/your docker server
6. get a dev database, and add this one to the docker_local folder as `startup.sql`
7. Run `docker-compose up` in the docker_local folder. 
8. Run `python manage.py migrate` for good measure
9. Run `python manage.py runserver`.

## Linting
The CI environment uses Flake8 for linting. The following command may work within pycharm, if you have flake8 installed (install the requirements again if you don't, it's one of the requirements now).
```flake8 . --ignore F401,E501,W503 --count --show-source --statistics --max-line-length=127 --exclude venv```
