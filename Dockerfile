FROM continuumio/anaconda3:2021.05
EXPOSE 3000
RUN apt-get update && \
    apt-get install -y apache2 \
    apache2-dev \
    vim \
 && apt-get clean \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /var/www/sentiment_analysis_text_classifier/
COPY ./ /var/www/sentiment_analysis_text_classifier/
RUN pip install -r requirements.txt
RUN /opt/conda/bin/mod_wsgi-express install-module
RUN mod_wsgi-express setup-server "/var/www/sentiment_analysis_text_classifier/source_code/sentiment_analysis.wsgi" --port=3000 \
    --user www-data --group www-data \
    --server-root=/etc/mod_wsgi-express-80
CMD ["/etc/mod_wsgi-express-80/apachectl", "start", "-D", "FOREGROUND"]