FROM debian:latest
EXPOSE 23

RUN DEBIAN_FRONTEND=noninteractive apt update 2> /dev/null 
RUN DEBIAN_FRONTEND=noninteractive apt -y install inetutils-telnetd libpam-script sudo 2> /dev/null

COPY ./pam_script_auth /usr/share/libpam-script/
COPY ./login /etc/pam.d

RUN chmod +x /usr/share/libpam-script/pam_script_auth
RUN echo 'telnet stream tcp nowait root /usr/sbin/tcpd     /usr/sbin/telnetd' >> /etc/inetd.conf

RUN echo 'pts/0:pts/1' >> /etc/securetty

# CMD [ "/usr/sbin/inetutils-inetd", "-d"]
