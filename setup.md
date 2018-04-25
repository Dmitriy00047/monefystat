You need to run postgresql server in docker
#setup
> sudo docker pull postgres:9.6
> sudo docker images
> sudo docker run --name postgresql96 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -h localhost -p 5432:5432 IMAGE_ID
> python3 -m pipenv install
> python3 -m pipenv shell
set environment variables for current session
> source secret.sh
> python3 manage.py