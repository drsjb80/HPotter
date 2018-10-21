FROM python:3.6
RUN mkdir -p /HPotter/hpotter
COPY hpotter /HPotter/hpotter
RUN cd /HPotter/hpotter && pip3 install -r requirements.txt
CMD cd /HPotter && python3 -m hpotter.hpotter
