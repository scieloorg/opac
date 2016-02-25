FROM centos:7

RUN yum install -y epel-release
RUN yum install -y python-pip python-devel gcc nginx git libxslt-devel libxml2-devel

RUN mkdir -p /var/www

WORKDIR /var/www

RUN git clone https://github.com/scieloorg/opac.git
RUN cp opac/instance/config.py.template opac/instance/config.py

RUN pip install -r opac/requirements.txt
RUN pip install -e git+https://git@github.com/scieloorg/opac_schema#egg=opac_schema

EXPOSE 5000
CMD cd opac && python manager.py runserver -h 0.0.0.0 -p 5000

