FROM python:3

WORKDIR /app
ADD . /app
RUN pip install pipenv
RUN pipenv install --dev
RUN pipenv run python manage.py
EXPOSE 4000
