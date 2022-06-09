FROM debian

RUN apt update
RUN apt install -y git vim python3 python3-pip libssl-dev rustc iptables

RUN git clone https://github.com/drsjb80/HPotter.git
RUN cd HPotter && git checkout dev && pip3 install -r requirements.txt
