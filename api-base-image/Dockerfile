# Parent image
FROM centos:7

LABEL description="HuBMAP Docker Base Image"

# Reduce the number of layers in image by minimizing the number of separate RUN commands
# 1 - Update the package listings
# 2 - Install git (for pip installing HuBMAP commons from github) and Extra Packages for Enterprise Linux (EPEL) 
# 3 - Use the EPEL repo for installing python, pip, uwsgi, uwsgi python plugin
# 4 - Upgrade pip, after upgrading, both pip and pip3 are the same version
# 5 - Clean all yum cache
RUN yum update -y && \
    yum install -y git epel-release && \
    yum install -y python36 python36-pip uwsgi uwsgi-plugin-python36.x86_64 && \
    pip3 install --upgrade pip && \
    yum clean all 

# Install gosu for de-elevating root to hubmap user
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.11/gosu-amd64" && \
    curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.11/gosu-amd64.asc" && \
    gpg --verify /usr/local/bin/gosu.asc && \
    rm /usr/local/bin/gosu.asc && \
    rm -r /root/.gnupg/ && \
    chmod +x /usr/local/bin/gosu
