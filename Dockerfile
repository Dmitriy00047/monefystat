FROM python:3

WORKDIR /app
ADD . /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80

CMD [ "python", "app.py" ]