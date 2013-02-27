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
import SocketServer
import logging.config
import threading
import time

import psycopg2

from ddsc_socket import settings
from ddsc_socket.celery import celery

SOCKS_SETTINGS = settings.SOCKS


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            conn = psycopg2.connect(dbname=SOCKS_SETTINGS['db_name'],
                user=SOCKS_SETTINGS['db_user'],
                password=SOCKS_SETTINGS['db_password'],
                host=SOCKS_SETTINGS['db_ip'])
            cur = conn.cursor()
        except:
            logger.error('database connection failed!')
        
        cur.execute("SELECT COUNT(*) FROM ddsc_core_ipaddress " +
            " WHERE label = " + '\'' + self.client_address[0] + '\'')

        if cur.fetchone()[0] < 1:
            logger.error('client IP: %r is not valid!'
                % self.client_address[0])
            return
        
        conn.close()
        cur.close()  # close database
        
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
            celery.send_task(
                "ddsc_worker.tasks.new_socket_detected",
                kwargs={
                    'pathDir': path,
                    'fileName': fileName + str(i) + '.csv'
                }
            )

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

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("ddsc_socket.socket_server")

logger.info(
    "Starting socket server on port {0}".format(SOCKS_SETTINGS['port'])
)
app = App()
app.run()
logger.warning("Threaded DDSC Socket Server is closed")
