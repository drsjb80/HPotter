FROM python:3.6
WORKDIR /HPotter
COPY . /HPotter
RUN cd /HPotter/hpotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m hpotter.hpotter
EXPOSE 8080
