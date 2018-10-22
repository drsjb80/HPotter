from datetime import datetime

qandr = {b'ls': 'foo\r\n', \
    b'more': 'bar\r\n', \
    b'date': datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y\r\n"), \
    b'dir': '/etc\r\n', \
    b'pwd': '/root\r\n'}
