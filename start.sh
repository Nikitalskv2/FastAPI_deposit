python3 -m venv env
. env/bin/activate
docker-compose up

#docker rm $(docker ps -aq)
#docker rmi --force $(docker images -q)