import asyncio
import time

from ntplib import NTPPacket, system_to_ntp_time, NTPException


class SNTPServer:
    PORT = 123
    BUFFER_SIZE = 1024
    LOCALHOST = '127.0.0.1'

    def __init__(self, delay):
        self.delay = delay
        self.loop = asyncio.get_event_loop()

    def run(self):
        class EchoServerProtocol:
            def connection_made(self, transport):
                self.transport = transport

            def datagram_received(self, data, address):
                receive_time = system_to_ntp_time(time.time())
                packet = NTPPacket()
                try:
                    packet.from_data(data)
                except NTPException:
                    print('Received not SNTP request')
                    return
                reply = self._get_reply(packet, receive_time)
                self.transport.sendto(reply, address)

            def _get_reply(self, packet: NTPPacket, receive_ts):
                send_packet = NTPPacket(version=3, mode=4)
                send_packet.stratum = 2
                send_packet.poll = 10
                send_packet.ref_timestamp = receive_ts - 5
                send_packet.set_origin_timestamp(*packet.get_tx_timestamp())
                send_packet.orig_timestamp = packet.tx_timestamp
                send_packet.recv_timestamp = receive_ts + delay
                send_packet.tx_timestamp = system_to_ntp_time(time.time()) + delay
                return send_packet.to_data()

        delay = self.delay
        listen = self.loop.create_datagram_endpoint(
            EchoServerProtocol, local_addr=(SNTPServer.LOCALHOST, SNTPServer.PORT))
        transport, protocol = self.loop.run_until_complete(listen)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        transport.close()
        self.loop.close()