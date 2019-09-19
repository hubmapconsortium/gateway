# Parent image
FROM centos:7

LABEL version="0.1.0"

# For using systemd
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;

WORKDIR /usr/src/app

# Copy from host to image
COPY . .

# Update packages
RUN yum update -y

# Install python 3.6
RUN yum install -y centos-release-scl
RUN yum install -y rh-python36

# Launch a new shell instance for python3.6
#RUN scl enable rh-python36 bash

# Install the development tools needed for compilation
RUN yum groupinstall -y "Development Tools"

# Upgrade pip
RUN ln -s /opt/rh/rh-python36/root/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip

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

# Enable nginx start at system boot time
RUN systemctl enable nginx

# Install app dependencies
RUN pip install -r src/requirements.txt

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
EXPOSE 5000 80 81

# Finally, we run uWSGI with the ini file
#CMD ["uwsgi", "--ini", "src/uwsgi.ini"]
CMD tail -f /dev/null