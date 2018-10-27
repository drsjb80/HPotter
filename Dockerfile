FROM alpine
RUN apk update
RUN apk add python3 
RUN pip3 install --upgrade pip
RUN apk add git
RUN apk add build-base
RUN apk add python3-dev
RUN apk add libffi-dev
RUN apk add openssl-dev
RUN mkdir -p /HPotter/hpotter
COPY hpotter /HPotter/hpotter
RUN cd /HPotter/hpotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m hpotter.hpotter
