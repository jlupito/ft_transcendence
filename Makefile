FILE=./docker-compose.yml

all : build

build :
	docker-compose -f $(FILE) build
	docker-compose -f $(FILE) up

clean :
	docker-compose -f $(FILE) down

fclean : clean
	docker system prune -af

re : fclean build
