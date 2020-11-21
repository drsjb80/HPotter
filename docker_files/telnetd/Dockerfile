FROM debian:latest
EXPOSE 23
RUN apt update && apt -y install inetutils-telnetd
RUN echo 'telnet stream tcp nowait root /usr/sbin/tcpd /usr/sbin/telnetd' >> /etc/inetd.conf
RUN useradd foo
RUN usermod -aG sudo foo
RUN echo 'foo:bar' | chpasswd
CMD ["/usr/sbin/inetutils-inetd","-d"]
