FILE=./docker-compose.yml

all : build

build :
	docker-compose -f $(FILE) build
	docker-compose -f $(FILE) up -d

clean :
	docker-compose -f $(FILE) down

fclean : clean
	docker stop $(docker ps -qa); 
	docker rm $(docker ps -qa); 
	docker rmi -f $(docker images -qa); 
	docker volume rm $(docker volume ls -q); 
	docker network rm $(docker network ls -q) 2>/dev/null
	docker system prune -af --volumes

re : fclean build
