# HuBMAP Hybrid Gateway Overview

This HuBMAP Gateway serves as an authentication and authorization gateway for some of the HuBMAP API services and File assets service, it also proxies the requests to the UI applications. 

HTTP requests to the following APIs will be proxied to this gateway service for authentication and authorization against Globus Auth before reaching to the target endpoints. 

- [Ingest API](https://github.com/hubmapconsortium/ingest-api)
- [Ontology API](https://github.com/hubmapconsortium/ontology-api) (currently only deployed on DEV and PROD)

And following are the APIs and UI applications that only use this gateway as reverse proxy without any authentication/authoriztion involved:

- [Antibody API](https://github.com/hubmapconsortium/antibody-api)
- [Ingest UI](https://github.com/hubmapconsortium/ingest-ui)
- [Portal UI](https://github.com/hubmapconsortium/portal-ui) (not for localhost build)

The file assets service is not an API per se, the gateway only does the auth cehck for requests made to

- `https://assets.hubmapconsortium.org/<uuid>/<relative-file-path>[?token=<globus-token>]`

Different from the above use cases, the following APIs are protected by AWS API Gateway with using Lambda Authorizors:

- [Entity API](https://github.com/hubmapconsortium/entity-api)
- [Search API](https://github.com/hubmapconsortium/search-api)
- [UUID API](https://github.com/hubmapconsortium/uuid-api)
- [Workspaces API](https://github.com/hubmapconsortium/user_workspaces_server) (only the REST API part on DEV and PROD)

More details are described in the [aws-api-gateway](https://github.com/hubmapconsortium/aws-api-gateway) repository.


## Overview of tools

- [Docker Engine](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

### Docker post-installation configurations

The Docker daemon binds to a Unix socket instead of a TCP port. By default that Unix socket is owned by the user root and other users can only access it using sudo. The Docker daemon always runs as the root user. If you don’t want to preface the docker command with sudo, add users to the `docker` group:

````
sudo usermod -aG docker $USER
````

Then log out and log back in so that your group membership is re-evaluated. If testing on a virtual machine, it may be necessary to restart the virtual machine for changes to take effect.

Note: the following instructions with docker commands are based on managing Docker as a non-root user.

## Docker build for local/DEV development

There are a few configurable environment variables to keep in mind:

- `COMMONS_BRANCH`: build argument only to be used during image creation when we need to use a branch of commons from github rather than the published PyPI package. Default to master branch if not set or null.
- `HOST_UID`: the user id on the host machine to be mapped to the container. Default to 1000 if not set or null.
- `HOST_GID`: the user's group id on the host machine to be mapped to the container. Default to 1000 if not set or null.

We can set and verify the environment variable like below:

````
export COMMONS_BRANCH=master
echo $COMMONS_BRANCH
````

Note: Environment variables set like this are only stored temporally. When you exit the running instance of bash by exiting the terminal, they get discarded. So for rebuilding the docker image, we'll need to make sure to set the environment variables again if necessary.

```
cd docker
./docker-development.sh [check|config|build|start|stop|down]
```

## Docker build for deployment on TEST/STAGE/PROD

```
cd docker
export HUBMAP_AUTH_API_VERSION=a.b.c (replace with the actual released version number)
./docker-deployment.sh [test|stage|prod] [start|stop|down]
```
