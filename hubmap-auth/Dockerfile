# Parent image
FROM centos:7

LABEL description="HuBMAP Authentication and Authorization Service" \
	version="1.0"

WORKDIR /usr/src/app

# Copy from host to image
COPY . .

# Nginx package from EPEL is old, we create a new repository file to install the latest mainline version of Nginx
RUN echo $'[nginx-mainline]\n\
name=nginx mainline repo\n\
baseurl=http://nginx.org/packages/mainline/centos/7/$basearch/\n\
gpgcheck=0\n\
enabled=1\n'\
>> /etc/yum.repos.d/nginx.repo

# Reduce the number of layers in image by minimizing the number of separate RUN commands
# 1 - Update the package listings
# 2 - Install nginx (using the custom yum repo specified earlier) and git (for pip installing HuBMAP commons from github)
# 3 - Remove the default nginx config file
# 4 - Install Extra Packages for Enterprise Linux (EPEL) 
# 5 - Use the EPEL repo for installing python, pip, uwsgi, uwsgi python plugin
# 6 - Upgrade pip, after upgrading, both pip and pip3 are the same version
# 7 - Install flask app dependencies with pip (pip3 also works)
# 8 - Make the start script executable
# 9 - Clean all yum cache
RUN yum update -y && \
    yum install -y nginx git && \
    rm /etc/nginx/conf.d/default.conf && \
    yum install -y epel-release && \
    yum install -y python36 python36-pip uwsgi uwsgi-plugin-python36.x86_64 && \
    pip3 install --upgrade pip && \
    pip install -r src/requirements.txt && \
    chmod +x start.sh && \
    yum clean all 

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
# Here 5000 is for the uwsgi socket, 80 for nginx
EXPOSE 5000 80

CMD ["./start.sh"]
