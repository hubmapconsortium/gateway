# Parent image
FROM centos:7

LABEL description="HuBMAP Docker Base Image" \
	version="1.0"

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

