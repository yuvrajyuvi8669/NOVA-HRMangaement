FROM rasa/rasa-sdk:2.8.4

WORKDIR /app

# COPY actions/requirements.txt ./

USER root

COPY ./actions /app/actions
COPY ./endpoints.yml /app

# RUN pip install -r requirements.txt
RUN pip install gevent
RUN pip install parsedatetime
RUN pip install urlvalidator
RUN pip install dateparser
RUN pip install xlrd
RUN pip install pyrsistent
RUN pip install spacy
EXPOSE 5009

USER 1000
CMD ["start","--actions","actions", "--port", "5009"]
