all: build up

build:
	docker-compose -f ./srcs/docker-compose.yml build

up:
	docker-compose -f ./srcs/docker-compose.yml up -d

logs:
	docker-compose -f ./srcs/docker-compose.yml logs

down:
	docker-compose -f ./srcs/docker-compose.yml down

clean:
	docker-compose -f ./srcs/docker-compose.yml down -v

fclean: clean
	@docker system prune -af

re: fclean all

.PHONY: all build up logs down clean re
