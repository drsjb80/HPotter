# Full Debian image running a telnet server that accepts ANY username/password.
# For lab / testing / CTF / honeypot use only -- telnet is cleartext and this
# image has authentication intentionally disabled. Do NOT expose it to a network
# you don't fully control.
#
# One-shot mode: the container accepts exactly ONE telnet session and then
# exits. Run it with `docker run --rm` and spawn a fresh container per
# connection (e.g. from your honeypot orchestrator).
FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        socat \
        inetutils-telnetd \
        telnet \
        login \
        ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Custom "login" program that accepts any username and any password.
COPY autologin.sh /usr/local/bin/autologin
RUN chmod +x /usr/local/bin/autologin

EXPOSE 23

# Accept a single TCP connection on :23, hand the raw socket to telnetd
# inetd-style (nofork = telnetd inherits the socket as its stdio), and exit
# when that session ends. No `fork` on TCP-LISTEN => exactly one connection.
CMD ["socat", "TCP-LISTEN:23,reuseaddr", "EXEC:/usr/sbin/telnetd -E /usr/local/bin/autologin,nofork"]
