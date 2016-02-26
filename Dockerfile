FROM centos:7

RUN yum install -y epel-release
RUN yum install -y python-pip python-devel gcc nginx git libxslt-devel libxml2-devel

RUN mkdir -p /var/www

WORKDIR /var/www

ADD . /var/www/opac
# RUN git clone https://github.com/scieloorg/opac.git
RUN cp opac/instance/config.py.template opac/instance/config.py

# dependêcias:
RUN pip install -r opac/requirements.txt
RUN pip install -r opac/requirements.production.txt

# serviço opac
RUN cp opac/deploy/opac_site.service /etc/systemd/system/opac_site.service
RUN systemctl start opac_site
RUN systemctl enable opac_site

# configuração nginx
RUN cp opac/deploy/opac_nginx.conf /etc/nginx/conf.d/opac.conf
RUN nginx -t
RUN systemctl start nginx
RUN systemctl enable nginx

# porta
EXPOSE 5000

CMD cd opac && python manager.py runserver -h 0.0.0.0 -p 5000

