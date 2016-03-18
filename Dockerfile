FROM centos:7

RUN yum install -y epel-release
RUN yum install -y python-pip python-devel gcc nginx git libxslt-devel libxml2-devel supervisor
RUN mkdir -p /var/www && mkdir -p /var/run/nginx

WORKDIR /var/www

COPY . /var/www/opac
VOLUME /var/www/opac/data
RUN chown -R nginx:nginx /var/www/opac
RUN cp opac/instance/config.py.template opac/instance/config.py

# dependêcias:
RUN pip install -r opac/requirements.txt && pip install -r opac/requirements.production.txt && pip install -r opac/requirements.dev.txt

# configuração nginx
RUN cat opac/deploy/nginx/opac_nginx.conf > /etc/nginx/nginx.conf && nginx -t

# configuração do serviço opac no supervisor
RUN cp opac/deploy/supervisord_opac.ini /etc/supervisord.d/opac.ini && supervisorctl start opac_gunicorn
RUN chown -R nginx:nginx /var/log/nginx && chown -R nginx:nginx /var/run/nginx

# portas
EXPOSE 8000
EXPOSE 8080

CMD supervisord -c /etc/supervisord.conf -n
