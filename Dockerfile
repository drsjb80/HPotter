FROM debian
RUN apt-get update
RUN apt-get -y install apt-utils
RUN apt-get -y install python3 
RUN apt-get -y install python3-pip
RUN apt-get -y install git
RUN git clone https://github.com/drsjb80/HPotter.git
RUN cd HPotter/src && pip3 install -r requirements.txt
EXPOSE 8080
CMD cd HPotter/src && python3 -m framework.main
