FROM debian
RUN apt-get update
RUN apt-get -y install python3 
RUN apt-get -y install python3-pip
RUN apt-get -y install git
RUN mkdir /HPotter
COPY hpotter /HPotter
RUN cd /HPotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m framework.main
