# HuBMAP Web Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication and authorization gateway for the HuBMAP API services. All API requests will be proxied to this gateway service for authentication and authorization before reaching to the API endpoints. As a result of this design, the API services no longer need to handle the authentication and authorization.

## Project structure

````
web-gateway-docker
├── docker-compose.yml
├── hubmap-auth
│   ├── Dockerfile
│   ├── log
│   ├── src
│   └── start.sh
├── nginx
│   ├── conf.d
│   └── html
└── sample-api
    ├── Dockerfile
    ├── log
    └── src
````

* `hubmap-auth` is the actual HuBMAP authentication and authorization service that verifies all the API requests.
* `nginx` is the folder used for mounting individual API config file and some static content, like favicon.ico.
* `sample-api` is an example API service.
* Each service has its own `Dockerfile`. 
* The `log` under each project is another volume mount, this allows us to access the log files generated from the running contianers on the host for easy debugging and monitoring.

To add new API service to the stack, you'll just need to follow the `sample-api` example, and add a new `conf` file (put it into `nginx/conf.d`) to instruct Nginx to handle the proxy pass by directing all the API requests to the `hubmap-auth` for authentication and authorization. And this is achieved through Nginx's `auth_request` module. That's also why each new sub-project will need to have Nginx componment.

## Overview of tools

- [Docker v19.03.2](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

## Workflow

We first use individual `Dockerfile` to define the image for each service componment. Then with Docker Compose, we define all the services and their relation to each other in the `docker-compose.yml` file. This allows us to spin this multi-container application stack up in a single command which does everything that needs to be done to get it running. 

Note: Don't confuse with the term of `service` and `container` when we talk about Docker Compose. A service only runs one image, but it codifies the way that image runs&mdash;what ports it should use, how many replicas of the container should run so the service has the capacity it needs, and so on. That's why in `docker-compose.yml` we see `services` defined.

In our `docker-compose.yml` configuration, you'll also see the `volumes` for each service. We use volumes to mount the app source code to the container when it's spun up and the log file generated on the containers are also made reachable by mounting to the host via volumes. 

### Build images

````
docker-compose build --no-cache
````

The command will go through all services in the `docker-compose.yml` file and build the ones that have a build section defined. 


### Start up services

````
docker-compose up
````

This command spins up all the containers defiened in the `docker-compose.yml` and aggregates the output of each container. When the command exits, all containers are stopped. Running `docker-compose up -d` starts the containers in the background and leaves them running.

Once the stack is up running, you'll be able to access the Sample API service at `http://localhost:8181/`. The Gateway is running at `http://localhost:8080` for API authentication and authorization purposes. 


### Stop the running services

````
docker-compose stop
````
The above command stops all the running containers without removing them. It preserves containers, volumes, and networks, along with every modification made to them. The stopped containers can be started again with `docker-compose start`. 

Instead of stopping all the containers, you can also specifically stop a particular service:

````
docker-compose stop <service-name>
````

### Restart services

````
docker-compose restart
````

This restarts all stopped and running services. If you make changes to your `docker-compose.yml` configuration or the individual `Dockerfile` these changes are not reflected after running this restart command. You'll need to rebuild all the images.

To just restart a particular service but not other services:

````
docker-compose restart <service-name>
````

### Reset the status of our project

````
docker-compose down
````

This command stops containers and removes containers, networks, volumes, and images created by `docker-compose up`.

You can take `down` 1 step further and add the `-v` flag to remove all volumes too. This is great for doing a full blown reset on your environment by running:

````
docker-compose down -v
````

## Debugging

We can list all running containers:

````
docker container ls
````

Then we can get into a container's shell by running:

````
docker exec -it <mycontainer> bash
````

