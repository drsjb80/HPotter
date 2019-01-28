# command:
# docker -p 22:22 -p 23:23 -p 8080:8080 -p 8000:8000 <image_name>

FROM alpine
RUN apk update
RUN apk add python3 
RUN pip3 install --upgrade pip
RUN apk add git
RUN apk add build-base
RUN apk add python3-dev
RUN apk add libffi-dev
RUN apk add openssl-dev
WORKDIR /HPotter
COPY . /HPotter
RUN cd /HPotter/hpotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m hpotter
# List plugin ports here
EXPOSE 22 23 80
