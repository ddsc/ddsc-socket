'''
Created on 14 nov. 2012
@author: LuS
Based on Python official document
20.17.4.3. Asynchronous Mixins
**** socket csv destination path
**** socket logging file path
**** socket host ip address and port
**** need to be set in django settings
'''
import threading
import SocketServer
import time
from ddsc_socket.celery import celery
import logging

from ddsc_socket import localsettings

SOCKS_SETTINGS = localsettings.SOCKS


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        logger.info("connection established with:  %r on port %r" %
                    (self.client_address[0], self.client_address[1]))
        first_time = time.time()
        current_time = time.time()
        timeout = SOCKS_SETTINGS['time_per_csv']  # in seconds
        path = SOCKS_SETTINGS['socket_dst']
        fileName = self.client_address[0] + '_' + \
            str(self.client_address[1]) + '_'
        i = 1
        keepLooping = True
        while keepLooping:
            f = open(path + fileName + str(i) + '.csv', 'wb')
            while timeout > (current_time - first_time) and keepLooping:
                try:
                    self.request.send("ok")
                    data = self.request.recv(1024)
                    f.write(data)
                    logger.debug("%r:%r wrote a line in %r" % (
                        self.client_address[0],
                        self.client_address[1], f))
                    current_time = time.time()
                except:
                    logger.info("connection with %r:%r lost" % (
                        self.client_address[0],
                        str(self.client_address[1])))
                    keepLooping = False
            f.close()    
            celery.send_task("ddsc_worker.importer.new_socket_detected", \
                kwargs={'pathDir': path, 'fileName': fileName + str(i) + '.csv'})

            i += 1
            first_time = time.time()
        f.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class App():
    def __init__(self):
        pass

    def run(self):
        #Main code goes here ...
        logger.info("Starting threaded DDSC Socket Server...")
        HOST, PORT = SOCKS_SETTINGS['host'], SOCKS_SETTINGS['port']
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        #server_thread.daemon = True
        server_thread.start()
        logger.info("Server loop running in thread:%r" % server_thread.name)
        while True:
            try:
                time.sleep(1000)
            except(KeyboardInterrupt):
                logger.warning("Socket server was shutdown by user.")
                server.shutdown()
                break

app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(SOCKS_SETTINGS['socks_logging'])
handler.setFormatter(formatter)
logger.addHandler(handler)

app.run()

logger.warning("Threaded DDSC Socket Server is closed")
