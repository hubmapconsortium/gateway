# HuBMAP Web Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication gateway for the HuBMAP API services. All access requests that require authentication will come to this gateway first. 

## Tools

- Docker v19.03.2: https://docs.docker.com/install/
- Docker Compose v3.7: https://docs.docker.com/compose/install/

## Build stack images with Docker Compose

````
docker-compose build --no-cache
````

The build subcommand will build all the images that are specified in the Compose file. The command will go through all services in the `docker-compose.yml` file and build the ones that have a build section defined. In our case, it will build two new images for `viz` and `nlp`.


## Start up the stack

````
docker-compose up
````

Then you will see the logs of the containers in stdout.

Once the stack is up running, you'll be able to access the Sample API service at http://localhost:8181/. The Gateway is running at http://localhost:8080 for API authentication and authorization purposes. 

If you want to run the containers in background:

````
docker-compose up -d
````

The `-d` option made the `docker-compose` command return.

## Stop or remove the containers

To safely stop the active services in the stack:

````
docker-compose stop
````
The above command will preserve containers, volumes, and networks, along with every modification made to them.

To reset the status of our project:

````
docker-compose down
````

The above command will stop your containers, and it also removes the stopped containers as well as any networks that were created.

You can take `down` 1 step further and add the `-v` flag to remove all volumes too. This is great for doing a full blown reset on your environment by running:

````
docker-compose down -v
````

## Debugging

We can list all running containers:

````
docker container ls
```

Then we can get into a container;s shell by running:

````
docker exec -it <mycontainer> bash
````

From inside the container, we can check the log file, etc...
