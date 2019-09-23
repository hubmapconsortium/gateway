# Parent image
FROM centos:7

LABEL version="0.1.0"

WORKDIR /usr/src/app

# Copy from host to image
COPY . .

# Update packages
RUN yum update -y

# Install development tools (gcc, make, etc.) needed for building software packages
RUN yum groupinstall -y "Development Tools"

# Install python 3.6 and pip via EPEL
# After installation, python3 and pip3 are available in shell
RUN yum install -y epel-release
RUN yum install -y python36 
RUN yum install -y python36-pip

# Upgrade pip
# After upgrade, both pip and pip3 are the same version
RUN pip3 install --upgrade pip

# Since uWSGI is provided by EPEL, there is no need to install it with pip
RUN yum install -y uwsgi 
# Install uWSGI plugin for Python 3.6 support
# Be sure to include the directive plugin = python36 in your uWSGI ini file
# This will install the Python 3.6 uWSGI plugin to : /usr/lib64/uwsgi/python3_plugin.so
RUN yum install -y uwsgi-plugin-python36.x86_64

# Nginx from EPEL is older version
# Install latest nginx by configuring nginx repo
RUN echo $'[nginx]\n\
name=nginx repo\n\
baseurl=http://nginx.org/packages/mainline/centos/7/$basearch/\n\
gpgcheck=0\n\
enabled=1\n'\
>> /etc/yum.repos.d/nginx.repo

RUN yum install -y nginx

# Remove the default config file
RUN rm /etc/nginx/conf.d/default.conf

# Install flask app dependencies
RUN pip install -r src/requirements.txt

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
# Here 5000 is for the uwsgi socket, 80 for flask app, 81 for sample-api
# Ports 80 and 81 will be mapped to 8080 and 8181 defiend in `docker-compose.yml` on the host
EXPOSE 5000 80 81

# Make the start script executable
RUN chmod +x start.sh

CMD ["./start.sh"]
