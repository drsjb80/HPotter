# command:
# docker -p 22:22 -p 23:23 -p 80:80 -p 8000:8000 <image_name>

FROM alpine
RUN apk update
RUN apk add python3 
RUN pip3 install --upgrade pip
RUN apk add git
RUN apk add build-base
RUN apk add python3-dev
RUN apk add libffi-dev
RUN apk add openssl-dev
RUN apk add mariadb
RUN apk add mariadb-dev
WORKDIR /HPotter
COPY hpotter /HPotter/hpotter/
COPY Dockerfile MANIFEST README.md requirements.txt setup.py /HPotter/
RUN cd /HPotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m hpotter.jsonserver &
CMD cd /HPotter && python3 -m hpotter
EXPOSE 22 23 80 8000


