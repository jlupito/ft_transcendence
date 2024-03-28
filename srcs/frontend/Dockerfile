FROM node:14-alpine

WORKDIR /app

COPY package*.json ./
COPY . /app

RUN npm install

RUN npm install bootstrap

EXPOSE 3000

CMD ["tail", "-f", "/dev/null"]
#la derniere instruction vise a maintenur le container ouvert
#a supprimer une fois le container fonctionnel
