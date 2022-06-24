FROM debian:latest
EXPOSE 23

RUN apt update && apt -y install inetutils-telnetd libpam-script sudo

COPY ./pam_script_auth /usr/share/libpam-script/
COPY ./login /etc/pam.d

RUN chmod +x /usr/share/libpam-script/pam_script_auth
RUN echo 'telnet stream tcp nowait root /usr/sbin/tcpd     /usr/sbin/telnetd' >> /etc/inetd.conf

RUN echo 'pts/0:pts/1' >> /etc/securetty

CMD [ "/usr/sbin/inetutils-inetd", "-d"]
