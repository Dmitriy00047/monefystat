FROM python:3

WORKDIR /app
ADD . /app
EXPOSE 80

CMD [ "python", "manage.py" ]