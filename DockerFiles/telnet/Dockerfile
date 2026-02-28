FROM debian:latest
LABEL org.opencontainers.image.authors="beatys@msudenver.edu"
EXPOSE 23

RUN apt update
RUN apt install inetutils-telnetd -y

COPY login /etc/pam.d/login
COPY telnet /etc/xinetd.d/telnet
