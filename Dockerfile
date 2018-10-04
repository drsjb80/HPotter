FROM alpine
RUN apk update
RUN apk add python3 
RUN apk add git
RUN mkdir -p /HPotter/hpotter
COPY hpotter /HPotter/hpotter
RUN cd /HPotter/hpotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m hpotter.hpotter
