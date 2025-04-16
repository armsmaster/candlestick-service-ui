# pull official base image
FROM node:23-alpine

# set work directory
WORKDIR /home/node/src/src/

# install dependencies
COPY ./src/package.json .
COPY ./src/package-lock.json .
RUN npm i

# copy project
COPY ./src/. .



