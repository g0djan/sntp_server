#!/usr/bin/env python3
from sntp_server import SNTPServer
import psutil
import signal


def main():
    print('Server start')
    free_port(SNTPServer.PORT)
    with open('config', 'r') as f:
        try:
            delay = int(f.read())
        except TypeError:
            print('File should contain only delay integer value')
            exit(1)
    sntp_server = SNTPServer(delay)
    sntp_server.run()


def free_port(port):
    for process in psutil.process_iter():
        for connection in process.connections(kind='inet'):
            if connection.laddr.port == port:
                process.send_signal(signal.SIGTERM)
                continue


if __name__ == '__main__':
    main()
