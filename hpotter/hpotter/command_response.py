

##
#
#   This data file holds basic commands for ssh and telnet.
#
#   Note: important to add date variable because a hacher will ensure the server shows the current date
#   Note: Shows correct output for date
#
##

from datetime import datetime


#todaysdate = time.strftime("%a %b %d %H:%M:%S %Y")

command_response = {
        'ls': 'Servers  Databases   Top_Secret  Documents\r\n',
        'ifconfig': 'lo: flags=75<UP,LOOPBACK,RUNNING> mtu 43386' \
                    '\r\n     inet 127.0.0.1 netmask 255.0.0.0' \
                    '\r\n     inet6 ::1 prefixlen 128 scopeid 0x10<host>' \
                    '\r\n     loop txquuelen 1000 (Local Loopback)' \
                    '\r\n     RX packets 4840 bytes 385124 (376.0 KiB)' \
                    '\r\n     RX errors 0 dropped 0 overruns 0 frame 0' \
                    '\r\n     TX packets 4840 bytes 364914 (447.0 KiB)' \
                    '\r\n     TX errors dropped 0 overruns 0 carrier 0 collisions 0'\
                    '\r\n     -------TEST---TEST----TEST-----TEST---------------------\r\n',

        'date': datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y\r\n"),
        'whoami': 'root\r\n',
        'netstat':  'Active Internet connections (w/o servers)' \
                    '\r\nProto Recv-Q Send-Q Local Address           Foreign Address         State' \
                    '\r\ntcp        0      0 localhost:51631         localhost:56104         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:60638         wf.networksolution:http TIME_WAIT' \
                    '\r\ntcp        0      0 localhost:42045         localhost:33768         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:34126         108.177.111.155:https   ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:51847         localhost:54690         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:35614         188.55.190.35.bc.:https ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:33745         localhost:40416         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:54690         localhost:51847         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:56104         localhost:51631         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:36219         localhost:37602         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:33768         localhost:42045         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:38395         localhost:38498         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:39459         localhost:48496         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:43453         localhost:42296         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:42216         localhost:60961         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:48496         localhost:39459         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:38770         localhost:54313         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:40416         localhost:33745         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:60961         localhost:42216         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:37602         localhost:36219         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:42296         localhost:43453         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:54313         localhost:38770         ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:59180         65.66.190.35.bc.g:https ESTABLISHED' \
                    '\r\ntcp        0      0 localhost:38498         localhost:38395         ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:43510         ik-in-x65.1e100.n:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:37046         sfo03s18-in-x04.1:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:38278         2607:f8b0:4001:c1:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:40212         2607:f8b0:4001:c1:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:32838         2607:f8b0:4001:c1:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:54650         2607:f8b0:4001:c0:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:57074         2607:f8b0:4001:c1:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:41774         ik-in-x84.1e100.n:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:47584         jd-in-x5e.1e100.n:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:41178         2607:f8b0:4001:c1:https ESTABLISHED' \
                    '\r\ntcp6       0      0 localhost:36818         2607:f8b0:4001:c0:https ESTABLISHED' \
                    '\r\nActive UNIX domain sockets (w/o servers)' \
                    '\r\nProto RefCnt Flags       Type       State         I-Node   Path' \
                    '\r\nunix  18     [ ]         DGRAM                    13596    /run/systemd/journal/dev-log' \
                    '\r\nunix  2      [ ]         DGRAM                    3669063  /run/wpa_supplicant/wlan0' \
                    '\r\nunix  2      [ ]         DGRAM                    3669068  /run/wpa_supplicant/p2p-dev-wlan0' \
                    '\r\nunix  2      [ ]         DGRAM                    23416    /run/user/0/systemd/notify' \
                    '\r\nunix  2      [ ]         DGRAM                    13176    /run/user/131/systemd/notify' \
                    '\r\nunix  2      [ ]         DGRAM                    14479    /run/systemd/journal/syslog' \
                    '\r\nunix  3      [ ]         DGRAM                    16862    /run/systemd/notify' \
                    '\r\nunix  8      [ ]         DGRAM                    16893    /run/systemd/journal/socket' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     28148    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     15319    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     13226    @/tmp/.X11-unix/X0' \
                    '\r\nunix  3      [ ]         DGRAM                    14013    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     31251    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27841    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3676259  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     25178    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24170    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     18291    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27212    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     30300    /var/run/dbus/system_bus_socket' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     28174    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     23219    @/tmp/dbus-CqGYXjGU' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     23999    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29994    ' \
                    '\r\nunix  2      [ ]         SEQPACKET  CONNECTED     3824104  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     31284    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24398    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24334    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     25967    ' \
                    '\r\nunix  2      [ ]         DGRAM                    23701    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     21575    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3931512  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3090558  /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     26153    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     31069    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     22522    /run/user/131/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     15318    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24623    ' \
                    '\r\nunix  2      [ ]         DGRAM                    19373    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     25125    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     30966    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27867    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3677056  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29293    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29170    ' \
                    '\r\nunix  3      [ ]         DGRAM                    15600    ' \
                    '\r\nunix  2      [ ]         DGRAM                    3665758  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24962    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     25662    /var/run/dbus/system_bus_socket' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     23785    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3673632  ' \
                    '\r\nunix  2      [ ]         DGRAM                    26754    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     17400    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3675266  /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29194    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     31071    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29001    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     22579    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24966    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27796    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24061    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     18389    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     12999    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     25121    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27031    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     22431    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     19362    /var/run/dbus/system_bus_socket' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     14187    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     19348    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     28173    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29707    /run/user/131/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     19355    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27881    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     26872    /run/user/131/pulse/native' \
                    '\r\nunix  3      [ ]         DGRAM                    13178    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3677053  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3088020  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24330    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24122    @/tmp/.X11-unix/X1' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     28147    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27020    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     26839    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27649    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     23743    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     14024    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     2351422  /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     29861    @/tmp/dbus-LJASGREu' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     13182    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     19778    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3676249  ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     3089201  /var/run/dbus/system_bus_socket' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     24321    /run/systemd/journal/stdout' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27847    ' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     30219    /run/user/0/bus' \
                    '\r\nunix  3      [ ]         STREAM     CONNECTED     27656    /run/systemd/journal/stdout\r\n',

        'find': ' \r\n',
        'ping': ' \r\n',
        'nslookup': '         \r\n',
        'ps': 'PID TTY          TIME CMD' \
                '\r\n831 tty1     00:00:01 Xorg' \
                '\r\n839 tty1     00:00:00 gnome-session-b' \
                '\r\n861 tty1     00:00:13 gnome-shell' \
                '\r\n1004 tty1     00:00:07 gsd-xsettings' \
                '\r\n1006 tty1     00:00:00 gsd-a11y-settin' \
                '\r\n1009 tty1     00:00:03 gsd-clipboard' \
                '\r\n1010 tty1     00:00:13 gsd-color' \
                '\r\n1012 tty1     00:00:00 gsd-datetime' \
                '\r\n1015 tty1     00:00:00 gsd-housekeepin' \
                '\r\n1016 tty1     00:00:03 gsd-keyboard' \
                '\r\n1021 tty1     00:00:03 gsd-media-keys' \
                '\r\n1022 tty1     00:00:00 gsd-mouse' \
                '\r\n1026 tty1     00:00:03 gsd-power' \
                '\r\n1032 tty1     00:00:00 gsd-print-notif' \
                '\r\n1033 tty1     00:00:00 gsd-rfkill' \
                '\r\n1039 tty1     00:00:00 gsd-screensaver' \
                '\r\n1041 tty1     00:00:00 gsd-sharing' \
                '\r\n1042 tty1     00:00:00 gsd-smartcard' \
                '\r\n1048 tty1     00:00:00 gsd-sound' \
                '\r\n1056 tty1     00:00:03 gsd-wacom' \
                '\r\n1153 tty2     00:13:49 Xorg' \
                '\r\n1162 tty2     00:00:00 gnome-session-b' \
                '\r\n1246 tty2     00:24:34 gnome-shell' \
                '\r\n1353 tty2     00:00:05 gsd-power' \
                '\r\n1355 tty2     00:00:00 gsd-print-notif' \
                '\r\n1356 tty2     00:00:00 gsd-rfkill' \
                '\r\n1357 tty2     00:00:00 gsd-screensaver' \
                '\r\n1358 tty2     00:00:21 gsd-sharing' \
                '\r\n1359 tty2     00:00:00 gsd-smartcard' \
                '\r\n1365 tty2     00:00:00 gsd-sound' \
                '\r\n1371 tty2     00:00:08 gsd-xsettings' \
                '\r\n1375 tty2     00:00:04 gsd-wacom' \
                '\r\n1385 tty2     00:00:00 gsd-a11y-settin' \
                '\r\n1386 tty2     00:00:04 gsd-clipboard' \
                '\r\n1389 tty2     00:00:16 gsd-color' \
                '\r\n1392 tty2     00:00:00 gsd-datetime' \
                '\r\n1394 tty2     00:00:00 gsd-housekeepin' \
                '\r\n1397 tty2     00:00:04 gsd-keyboard' \
                '\r\n1402 tty2     00:00:04 gsd-media-keys' \
                '\r\n1403 tty2     00:00:00 gsd-mouse' \
                '\r\n1417 tty2     00:00:00 gsd-printer' \
                '\r\n1460 tty2     00:00:00 gsd-disk-utilit' \
                '\r\n1462 tty2     00:00:12 gnome-software' \
                '\r\n1468 tty2     00:00:04 tracker-miner-f' \
                '\r\n1469 tty2     00:00:02 tracker-extract' \
                '\r\n1471 tty2     00:00:04 evolution-alarm' \
                '\r\n1476 tty2     00:00:00 tracker-miner-a' \
                '\r\n3627 tty2     00:37:01 firefox-esr' \
                '\r\n3788 tty2     00:03:30 Web Content' \
                '\r\n4101 tty2     01:18:47 Web Content' \
                '\r\n6289 tty2     00:04:44 Web Content' \
                '\r\n6332 tty2     00:07:45 Web Content' \
                '\r\n10009 pts/1    00:00:03 vim' \
                '\r\n10126 pts/2    00:00:00 ps\r\n',

        'ps -a': 'PID TTY          TIME CMD' \
                '\r\n831 tty1     00:00:01 Xorg' \
                '\r\n839 tty1     00:00:00 gnome-session-b' \
                '\r\n861 tty1     00:00:13 gnome-shell' \
                '\r\n1004 tty1     00:00:07 gsd-xsettings' \
                '\r\n1006 tty1     00:00:00 gsd-a11y-settin' \
                '\r\n1009 tty1     00:00:03 gsd-clipboard' \
                '\r\n1010 tty1     00:00:13 gsd-color' \
                '\r\n1012 tty1     00:00:00 gsd-datetime' \
                '\r\n1015 tty1     00:00:00 gsd-housekeepin' \
                '\r\n1016 tty1     00:00:03 gsd-keyboard' \
                '\r\n1021 tty1     00:00:03 gsd-media-keys' \
                '\r\n1022 tty1     00:00:00 gsd-mouse' \
                '\r\n1026 tty1     00:00:03 gsd-power' \
                '\r\n1032 tty1     00:00:00 gsd-print-notif' \
                '\r\n1033 tty1     00:00:00 gsd-rfkill' \
                '\r\n1039 tty1     00:00:00 gsd-screensaver' \
                '\r\n1041 tty1     00:00:00 gsd-sharing' \
                '\r\n1042 tty1     00:00:00 gsd-smartcard' \
                '\r\n1048 tty1     00:00:00 gsd-sound' \
                '\r\n1056 tty1     00:00:03 gsd-wacom' \
                '\r\n1153 tty2     00:13:49 Xorg' \
                '\r\n1162 tty2     00:00:00 gnome-session-b' \
                '\r\n1246 tty2     00:24:34 gnome-shell' \
                '\r\n1353 tty2     00:00:05 gsd-power' \
                '\r\n1355 tty2     00:00:00 gsd-print-notif' \
                '\r\n1356 tty2     00:00:00 gsd-rfkill' \
                '\r\n1357 tty2     00:00:00 gsd-screensaver' \
                '\r\n1358 tty2     00:00:21 gsd-sharing' \
                '\r\n1359 tty2     00:00:00 gsd-smartcard' \
                '\r\n1365 tty2     00:00:00 gsd-sound' \
                '\r\n1371 tty2     00:00:08 gsd-xsettings' \
                '\r\n1375 tty2     00:00:04 gsd-wacom' \
                '\r\n1385 tty2     00:00:00 gsd-a11y-settin' \
                '\r\n1386 tty2     00:00:04 gsd-clipboard' \
                '\r\n1389 tty2     00:00:16 gsd-color' \
                '\r\n1392 tty2     00:00:00 gsd-datetime' \
                '\r\n1394 tty2     00:00:00 gsd-housekeepin' \
                '\r\n1397 tty2     00:00:04 gsd-keyboard' \
                '\r\n1402 tty2     00:00:04 gsd-media-keys' \
                '\r\n1403 tty2     00:00:00 gsd-mouse' \
                '\r\n1417 tty2     00:00:00 gsd-printer' \
                '\r\n1460 tty2     00:00:00 gsd-disk-utilit' \
                '\r\n1462 tty2     00:00:12 gnome-software' \
                '\r\n1468 tty2     00:00:04 tracker-miner-f' \
                '\r\n1469 tty2     00:00:02 tracker-extract' \
                '\r\n1471 tty2     00:00:04 evolution-alarm' \
                '\r\n1476 tty2     00:00:00 tracker-miner-a' \
                '\r\n3627 tty2     00:37:01 firefox-esr' \
                '\r\n3788 tty2     00:03:30 Web Content' \
                '\r\n4101 tty2     01:18:47 Web Content' \
                '\r\n6289 tty2     00:04:44 Web Content' \
                '\r\n6332 tty2     00:07:45 Web Content' \
                '\r\n10009 pts/1    00:00:03 vim' \
                '\r\n10126 pts/2    00:00:00 ps\r\n',

        'vi /etc/shadow': 'root:$1$/avpfBJ1$x0z8w5UF9Iv./DR9E9Lid.:14747:0:99999:7:::' \
                            '\r\ndaemon:*:14684:0:99999:7:::' \
                            '\r\nbin:*:14684:0:99999:7:::' \
                            '\r\nsys:$1$fUX6BPOt$Miyc3UpOzQJqz4s5wFD9l0:14742:0:99999:7:::' \
                            '\r\nsync:*:14684:0:99999:7:::' \
                            '\r\ngames:*:14684:0:99999:7:::' \
                            '\r\nman:*:14684:0:99999:7:::' \
                            '\r\nlp:*:14684:0:99999:7:::' \
                            '\r\nmail:*:14684:0:99999:7:::' \
                            '\r\nnews:*:14684:0:99999:7:::' \
                            '\r\nuucp:*:14684:0:99999:7:::' \
                            '\r\nproxy:*:14684:0:99999:7:::' \
                            '\r\nwww-data:*:14684:0:99999:7:::' \
                            '\r\nbackup:*:14684:0:99999:7:::' \
                            '\r\nlist:*:14684:0:99999:7:::' \
                            '\r\nirc:*:14684:0:99999:7:::' \
                            '\r\ngnats:*:14684:0:99999:7:::' \
                            '\r\nnobody:*:14684:0:99999:7:::' \
                            '\r\nlibuuid:!:14684:0:99999:7:::' \
                            '\r\ndhcp:*:14684:0:99999:7:::' \
                            '\r\nsyslog:*:14684:0:99999:7:::' \
                            '\r\nklog:$1$f2ZVMS4K$R9XkI.CmLdHhdUE3X9jqP0:14742:0:99999:7:::' \
                            '\r\nsshd:*:14684:0:99999:7:::' \
                            '\r\nmsfadmin:$1$XN10Zj2c$Rt/zzCW3mLtUWA.ihZjA5/:14684:0:99999:7:::' \
                            '\r\nbind:*:14685:0:99999:7:::' \
                            '\r\npostfix:*:14685:0:99999:7:::' \
                            '\r\nftp:*:14685:0:99999:7:::' \
                            '\r\npostgres:$1$Rw35ik.x$MgQgZUuO5pAoUvfJhfcYe/:14685:0:99999:7:::' \
                            '\r\nmysql:!:14685:0:99999:7:::' \
                            '\r\ntomcat55:*:14691:0:99999:7:::' \
                            '\r\ndistccd:*:14698:0:99999:7:::' \
                            '\r\nuser:$1$HESu9xrH$k.o3G93DGoXIiQKkPmUgZ0:14699:0:99999:7:::' \
                            '\r\nservice:$1$kR3ue7JZ$7GxELDupr5Ohp6cjZ3Bu//:14715:0:99999:7:::' \
                            '\r\ntelnetd:*:14715:0:99999:7:::' \
                            '\r\nproftpd:!:14727:0:99999:7:::' \
                            '\r\nstatd:*:15474:0:99999:7:::' \
                            '\r\nsnmp:*:15480:0:99999:7:::' \
                            '\r\nskywalker:$1$OHklYwhp$vwtbf4vho8RcuLUlYv9rL1:17741:0:99999:7:::\r\n' ,

        'vi /etc/passwd': '\r\nroot:x:0:0:root:/root:/bin/bash' \
                            '\r\ndaemon:x:1:1:daemon:/usr/sbin:/bin/sh' \
                            '\r\nbin:x:2:2:bin:/bin:/bin/sh' \
                            '\r\nsys:x:3:3:sys:/dev:/bin/sh' \
                            '\r\nsync:x:4:65534:sync:/bin:/bin/sync' \
                            '\r\ngames:x:5:60:games:/usr/games:/bin/sh' \
                            '\r\nman:x:6:12:man:/var/cache/man:/bin/sh' \
                            '\r\nlp:x:7:7:lp:/var/spool/lpd:/bin/sh' \
                            '\r\nmail:x:8:8:mail:/var/mail:/bin/sh' \
                            '\r\nnews:x:9:9:news:/var/spool/news:/bin/sh' \
                            '\r\nuucp:x:10:10:uucp:/var/spool/uucp:/bin/sh' \
                            '\r\nproxy:x:13:13:proxy:/bin:/bin/sh' \
                            '\r\nwww-data:x:33:33:www-data:/var/www:/bin/sh' \
                            '\r\nbackup:x:34:34:backup:/var/backups:/bin/sh' \
                            '\r\nlist:x:38:38:Mailing List Manager:/var/list:/bin/sh' \
                            '\r\nirc:x:39:39:ircd:/var/run/ircd:/bin/sh' \
                            '\r\ngnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/bin/sh' \
                            '\r\nnobody:x:65534:65534:nobody:/nonexistent:/bin/sh' \
                            '\r\nlibuuid:x:100:101::/var/lib/libuuid:/bin/sh' \
                            '\r\ndhcp:x:101:102::/nonexistent:/bin/false' \
                            '\r\nsyslog:x:102:103::/home/syslog:/bin/false' \
                            '\r\nklog:x:103:104::/home/klog:/bin/false' \
                            '\r\nsshd:x:104:65534::/var/run/sshd:/usr/sbin/nologin' \
                            '\r\nmsfadmin:x:1000:1000:msfadmin,,,:/home/msfadmin:/bin/bash' \
                            '\r\nbind:x:105:113::/var/cache/bind:/bin/false' \
                            '\r\npostfix:x:106:115::/var/spool/postfix:/bin/false' \
                            '\r\nftp:x:107:65534::/home/ftp:/bin/false' \
                            '\r\npostgres:x:108:117:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash' \
                            '\r\nmysql:x:109:118:MySQL Server,,,:/var/lib/mysql:/bin/false' \
                            '\r\ntomcat55:x:110:65534::/usr/share/tomcat5.5:/bin/false' \
                            '\r\ndistccd:x:111:65534::/:/bin/false' \
                            '\r\nuser:x:1001:1001:just a user,111,,:/home/user:/bin/bash' \
                            '\r\nservice:x:1002:1002:,,,:/home/service:/bin/bash' \
                            '\r\ntelnetd:x:112:120::/nonexistent:/bin/false' \
                            '\r\nproftpd:x:113:65534::/var/run/proftpd:/bin/false' \
                            '\r\nstatd:x:114:65534::/var/lib/nfs:/bin/false' \
                            '\r\nsnmp:x:115:65534::/var/lib/snmp:/bin/false' \
                            '\r\nskywalker:x:1003:1003::/home/skywalker:/bin/sh\r\n',

            'uname': 'Linux\r\n',
            'uname -n': 'AmericanExpress.com\r\n',
            'uname -v': '64-Ubuntu SMP Mon Sep 22 21:28:38 UTC 2014\r\n',
            'uname': 'Linux\r\n',
            'uname -n': 'AmericanExpress.com\r\n',
            'uname -v': '64-Ubuntu SMP Mon Sep 22 21:28:38 UTC 2014\r\n',
            'sudo lshw': 'localhost.localdomain'
    '\r\n   description: Computer' \
    '\r\n   product: VirtualBox'
    '\r\n   vendor: innotek GmbH'
    '\r\n   version: 1.2'
    '\r\n   serial: 0'
    '\r\n   width: 64 bits'
    '\r\n   capabilities: smbios-2.5 dmi-2.5 smp vsyscall32'
    '\r\n   configuration: family=Virtual Machine uuid=CEE1DFD6-0C1F-4CC1-934C-1B8DB10409F7'
    '\r\n *-core'
    '\r\n      description: Motherboard'
    '\r\n      product: VirtualBox'
    '\r\n      vendor: Oracle Corporation'
    '\r\n      physical id: 0'
    '\r\n      version: 1.2'
    '\r\n      serial: 0'
    '\r\n    *-firmware'
    '\r\n         description: BIOS'
    '\r\n         vendor: innotek GmbH'
    '\r\n         physical id: 0'
    '\r\n         version: VirtualBox'
    '\r\n         date: 12/01/2006'
    '\r\n         size: 128KiB'
    '\r\n         capacity: 128KiB'
    '\r\n         capabilities: isa pci cdboot bootselect int9keyboard int10video acpi'
    '\r\n    *-memory'
    '\r\n         description: System memory'
    '\r\n         physical id: 1'
    '\r\n         size: 8GiB'
    '\r\n    *-cpu'
    '\r\n         product: Intel(R) Core(TM) i7-5820K CPU @ 3.30GHz'
    '\r\n         vendor: Intel Corp.'
    '\r\n         vendor_id: GenuineIntel'
    '\r\n         physical id: 2'
    '\r\n         bus info: cpu@0'
    '\r\n         width: 64 bits'
    '\r\n         capabilities: fpu fpu_exception wp vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx rdtscp x86-64 constant_tsc rep_good nopl xtopology nonstop_tsc eagerfpu pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx rdrand hypervisor lahf_lm abm fsgsbase avx2 invpcid'
    '\r\n    *-pci'
    '\r\n         description: Host bridge'
    '\r\n         product: 440FX - 82441FX PMC [Natoma]'
    '\r\n         vendor: Intel Corporation'
    '\r\n         physical id: 100'
    '\r\n         bus info: pci@0000:00:00.0'
    '\r\n         version: 02'
    '\r\n         width: 32 bits'
    '\r\n         clock: 33MHz'
    '\r\n       *-isa'
    '\r\n            description: ISA bridge'
    '\r\n            product: 82371SB PIIX3 ISA [Natoma/Triton II]'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: 1'
    '\r\n            bus info: pci@0000:00:01.0'
    '\r\n            version: 00'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: isa bus_master'
    '\r\n            configuration: latency=0'
    '\r\n       *-ide'
    '\r\n            description: IDE interface'
    '\r\n            product: 82371AB/EB/MB PIIX4 IDE'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: 1.1'
    '\r\n            bus info: pci@0000:00:01.1'
    '\r\n            logical name: scsi2'
    '\r\n            version: 01'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: ide bus_master emulated'
    '\r\n            configuration: driver=ata_piix latency=64'
    '\r\n            resources: irq:0 ioport:1f0(size=8) ioport:3f6 ioport:170(size=8) ioport:376 ioport:d000(size=16)'
    '\r\n          *-cdrom'
    '\r\n               description: DVD reader'
    '\r\n               product: CD-ROM'
    '\r\n               vendor: VBOX'
    '\r\n               physical id: 0.0.0'
    '\r\n               bus info: scsi@2:0.0.0'
    '\r\n               logical name: /dev/cdrom'
    '\r\n               logical name: /dev/sr0'
    '\r\n               logical name: /run/media/bhudson/VBox_GAs_5.2.20'
    '\r\n               version: 1.0'
    '\r\n               capabilities: removable audio dvd'
    '\r\n               configuration: ansiversion=5 mount.fstype=iso9660 mount.options=ro,nosuid,nodev,relatime,uid=1000,gid=1000,iocharset=utf8,mode=0400,dmode=0500 state=mounted status=ready'
    '\r\n             *-medium'
    '\r\n                  physical id: 0'
    '\r\n                  logical name: /dev/cdrom'
    '\r\n                  logical name: /run/media/bhudson/VBox_GAs_5.2.20'
    '\r\n                  configuration: mount.fstype=iso9660 mount.options=ro,nosuid,nodev,relatime,uid=1000,gid=1000,iocharset=utf8,mode=0400,dmode=0500 state=mounted'
    '\r\n       *-display'
    '\r\n            description: VGA compatible controller'
    '\r\n            product: VirtualBox Graphics Adapter'
    '\r\n            vendor: InnoTek Systemberatung GmbH'
    '\r\n            physical id: 2'
    '\r\n            bus info: pci@0000:00:02.0'
    '\r\n            version: 00'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: vga_controller rom'
    '\r\n            configuration: driver=vboxvideo latency=0'
    '\r\n            resources: irq:18 memory:e0000000-e7ffffff'
    '\r\n       *-network'
    '\r\n            description: Ethernet interface'
    '\r\n            product: 82540EM Gigabit Ethernet Controller'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: 3'
    '\r\n            bus info: pci@0000:00:03.0'
    '\r\n            logical name: enp0s3'
    '\r\n            version: 02'
    '\r\n            serial: 08:00:27:ad:5f:e1'
    '\r\n            size: 1Gbit/s'
    '\r\n            capacity: 1Gbit/s'
    '\r\n            width: 32 bits'
    '\r\n            clock: 66MHz'
    '\r\n            capabilities: pm pcix bus_master cap_list ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation'
    '\r\n            configuration: autonegotiation=on broadcast=yes driver=e1000 driverversion=7.3.21-k8-NAPI duplex=full ip=10.0.2.15 latency=64 link=yes mingnt=255 multicast=yes port=twisted pair speed=1Gbit/s'
    '\r\n            resources: irq:19 memory:f0000000-f001ffff ioport:d010(size=8)'
    '\r\n       *-generic'
    '\r\n            description: System peripheral'
    '\r\n            product: VirtualBox Guest Service'
    '\r\n            vendor: InnoTek Systemberatung GmbH'
    '\r\n            physical id: 4'
    '\r\n            bus info: pci@0000:00:04.0'
    '\r\n            version: 00'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            configuration: driver=vboxguest latency=0'
    '\r\n            resources: irq:20 ioport:d020(size=32) memory:f0400000-f07fffff memory:f0800000-f0803fff'
    '\r\n       *-multimedia'
    '\r\n            description: Multimedia audio controller'
    '\r\n            product: 82801AA AC97 Audio Controller'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: 5'
    '\r\n            bus info: pci@0000:00:05.0'
    '\r\n            version: 01'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: bus_master'
    '\r\n            configuration: driver=snd_intel8x0 latency=64'
    '\r\n            resources: irq:21 ioport:d100(size=256) ioport:d200(size=64)'
    '\r\n       *-usb:0'
    '\r\n            description: USB controller'
    '\r\n            product: KeyLargo/Intrepid USB'
    '\r\n            vendor: Apple Inc.'
    '\r\n            physical id: 6'
    '\r\n            bus info: pci@0000:00:06.0'
    '\r\n            version: 00'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: ohci bus_master cap_list'
    '\r\n            configuration: driver=ohci-pci latency=64'
    '\r\n            resources: irq:22 memory:f0804000-f0804fff'
    '\r\n          *-usbhost'
    '\r\n               product: OHCI PCI host controller'
    '\r\n               vendor: Linux 3.10.0-862.9.1.el7.x86_64 ohci_hcd'
    '\r\n               physical id: 1'
    '\r\n               bus info: usb@2'
    '\r\n               logical name: usb2'
    '\r\n               version: 3.10'
    '\r\n               capabilities: usb-1.10'
    '\r\n               configuration: driver=hub slots=12 speed=12Mbit/s'
    '\r\n       *-bridge'
    '\r\n            description: Bridge'
    '\r\n            product: 82371AB/EB/MB PIIX4 ACPI'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: 7'
    '\r\n            bus info: pci@0000:00:07.0'
    '\r\n            version: 08'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: bridge'
    '\r\n            configuration: driver=piix4_smbus latency=0'
    '\r\n            resources: irq:9'
    '\r\n       *-usb:1'
    '\r\n            description: USB controller'
    '\r\n            product: 82801FB/FBM/FR/FW/FRW (ICH6 Family) USB2 EHCI Controller'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: b'
    '\r\n            bus info: pci@0000:00:0b.0'
    '\r\n            version: 00'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: ehci bus_master cap_list'
    '\r\n            configuration: driver=ehci-pci latency=64'
    '\r\n            resources: irq:19 memory:f0805000-f0805fff'
    '\r\n          *-usbhost'
    '\r\n               product: EHCI Host Controller'
    '\r\n               vendor: Linux 3.10.0-862.9.1.el7.x86_64 ehci_hcd'
    '\r\n               physical id: 1'
    '\r\n               bus info: usb@1'
    '\r\n               logical name: usb1'
    '\r\n               version: 3.10'
    '\r\n               capabilities: usb-2.00'
    '\r\n               configuration: driver=hub slots=12 speed=480Mbit/s'
    '\r\n       *-sata'
    '\r\n            description: SATA controller'
    '\r\n            product: 82801HM/HEM (ICH8M/ICH8M-E) SATA Controller [AHCI mode]'
    '\r\n            vendor: Intel Corporation'
    '\r\n            physical id: d'
    '\r\n            bus info: pci@0000:00:0d.0'
    '\r\n            logical name: scsi0'
    '\r\n            version: 02'
    '\r\n            width: 32 bits'
    '\r\n            clock: 33MHz'
    '\r\n            capabilities: sata pm ahci_1.0 bus_master cap_list emulated'
    '\r\n            configuration: driver=ahci latency=64'
    '\r\n            resources: irq:21 ioport:d240(size=8) ioport:d248(size=4) ioport:d250(size=8) ioport:d258(size=4) ioport:d260(size=16) memory:f0806000-f0807fff'
    '\r\n          *-disk'
    '\r\n               description: ATA Disk'
    '\r\n               product: VBOX HARDDISK'
    '\r\n               vendor: VirtualBox'
    '\r\n               physical id: 0.0.0'
    '\r\n               bus info: scsi@0:0.0.0'
    '\r\n               logical name: /dev/sda'
    '\r\n               version: 1.0'
    '\r\n               serial: VB9b21dcc5-1c533658'
    '\r\n               size: 20GiB (21GB)'
    '\r\n               capabilities: partitioned partitioned:dos'
    '\r\n               configuration: ansiversion=5 logicalsectorsize=512 sectorsize=512 signature=00092a62'
    '\r\n             *-volume:0'
    '\r\n                  description: Linux filesystem partition'
    '\r\n                  physical id: 1'
    '\r\n                  bus info: scsi@0:0.0.0,1'
    '\r\n                  logical name: /dev/sda1'
    '\r\n                  logical name: /boot'
    '\r\n                  capacity: 1GiB'
    '\r\n                  capabilities: primary bootable'
    '\r\n                  configuration: mount.fstype=xfs mount.options=rw,seclabel,relatime,attr2,inode64,noquota state=mounted'
    '\r\n             *-volume:1'
    '\r\n                  description: Linux LVM Physical Volume partition'
    '\r\n                  physical id: 2'
    '\r\n                  bus info: scsi@0:0.0.0,2'
    '\r\n                  logical name: /dev/sda2'
    '\r\n                  serial: nDlHKR-UFWs-zidt-eydu-lcnU-YCDZ-B0qRaw'
    '\r\n                  size: 18GiB'
    '\r\n                  capacity: 18GiB'
    '\r\n                  capabilities: primary multi lvm2'
    '\r\n    *-pnp00:00'
    '\r\n         product: PnP device PNP0303'
    '\r\n         physical id: 3'
    '\r\n         capabilities: pnp'
    '\r\n         configuration: driver=i8042 kbd'
    '\r\n    *-pnp00:01'
    '\r\n         product: PnP device PNP0f03'
    '\r\n         physical id: 4'
    '\r\n         capabilities: pnp'
    '\r\n         configuration: driver=i8042 aux'
    '\r\n *-network:0 DISABLED'
    '\r\n      description: Ethernet interface'
    '\r\n      physical id: 1'
    '\r\n      logical name: virbr0-nic'
    '\r\n      serial: 52:54:00:60:36:cc'
    '\r\n      size: 10Mbit/s'
    '\r\n      capabilities: ethernet physical'
    '\r\n      configuration: autonegotiation=off broadcast=yes driver=tun driverversion=1.6 duplex=full link=no multicast=yes port=twisted pair speed=10Mbit/s'
    '\r\n *-network:1'
    '\r\n      description: Ethernet interface'
    '\r\n      physical id: 2'
    '\r\n      logical name: virbr0'
    '\r\n      serial: 52:54:00:60:36:cc'
    '\r\n      capabilities: ethernet physical'
    '\r\n      configuration: broadcast=yes driver=bridge driverversion=2.3 firmware=N/A ip=192.168.122.1 link=no multicast=yes\r\n',




        }
