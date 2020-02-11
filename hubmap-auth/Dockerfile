# Parent image
FROM hubmap/api-base-image:latest

LABEL description="HuBMAP Authentication and Authorization Service"

# Add the hubmap user UID:9000, GID:9000
# Add hubmap to sudoers
RUN groupadd --gid 9000 hubmap && \
    useradd --uid 9000 --gid 9000 hubmap && \
    usermod -aG wheel hubmap

# Require no password for hubmap sudo
COPY sudoers.txt /etc/sudoers

# Nginx package from EPEL is old, we create a new repository file to install the latest mainline version of Nginx
RUN echo $'[nginx-mainline]\n\
name=nginx mainline repo\n\
baseurl=http://nginx.org/packages/mainline/centos/7/$basearch/\n\
gpgcheck=0\n\
enabled=1\n'\
>> /etc/yum.repos.d/nginx.repo

# Reduce the number of layers in image by minimizing the number of separate RUN commands
# 1 - Update the package listings
# 2 - Install nginx (using the custom yum repo specified earlier) and sudo
# 3 - Remove the default nginx config file
# 4 - Clean all yum cache
RUN yum update -y && \
    yum install -y nginx sudo && \
    rm /etc/nginx/conf.d/default.conf && \
    yum clean all 

# Specify the user to execute all commands below
USER hubmap

# Change dir to avoid permission issue
WORKDIR /home/hubmap

# Copy from host to image
COPY . .

# 1 - Install flask app dependencies with pip (pip3 also works)
# 2 - Change ownership of the start script
# 3 - Make the start script executable
RUN sudo pip install -r src/requirements.txt && \
    sudo chown hubmap:hubmap start.sh && \
    chmod +x start.sh

# Create directories for data and logs mounted volumes
RUN mkdir data && \
    mkdir logs

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
# Here 5000 is for the uwsgi socket, 80 for nginx
EXPOSE 5000 80

CMD ["./start.sh"]
