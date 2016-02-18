# (c) Fugro GeoServices, Nelen & Schuurmans. MIT licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
import SocketServer
import errno
import logging.config
import os
import socket

import psycopg2
import pytz

from ddsc_socket import settings
from ddsc_socket.celery import celery

logger = logging.getLogger(__name__)

BUFSIZE = 1024  # bytes
SQL = "SELECT count(1) FROM lizard_nxt_ipmapping WHERE ip_address = '{}';"

CONNEW = "Client connecting from %s:%d."
CONEND = "Connection with %s:%d lost."
UNAUTH = "Will not serve %s:%d (unauthorized)."


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def _get_data(self):
        """Return the data send by a client.

        What is currently lacking, is some kind of "EOF" command the client
        can send to signal end-of-file.

        NB: a connection closed by a client does not always result in a
        socket.error. In that case, data is an empty string.

        """
        try:
            self.request.send("ok")
            data = self.request.recv(BUFSIZE)  # BLOCKING
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                logger.info(CONEND, self.ip, self.port)
            else:
                logger.error(e)
            data = ''
        else:
            if not data:
                logger.info(CONEND, self.ip, self.port)
        finally:
            return data

    def handle(self):

        self.ip, self.port = self.client_address
        logger.info(CONNEW, self.ip, self.port)

        try:
            conn, cur = None, None
            conn = psycopg2.connect(**settings.DATABASE)
            cur = conn.cursor()
            cur.execute(SQL.format(self.ip))
            count = cur.fetchone()[0]
        except Exception as e:
            logger.error(e)
            return
        finally:
            if cur and not cur.closed:
                cur.close()
            if conn and not conn.closed:
                conn.close()

        if count < 1:
            logger.warning(UNAUTH, self.ip, self.port)
            return

        data = self._get_data()
        if not data:
            return

        utc = datetime.now(pytz.utc).isoformat()
        filename = "{}_{}.csv".format(self.ip, utc)
        file_path = os.path.join(settings.DIR, filename)

        # TODO: implement a timeout.
        # TODO: implement a rolling file.

        with open(file_path, 'wb') as f:
            logger.info("Writing data to %s", file_path)
            f.write(data)
            while True:
                data = self._get_data()
                if data:
                    f.write(data)
                else:
                    break

        TASK = "lizard_nxt.tasks.import_socket_timeseries_from_csv"
        logger.info("Sending task to Celery: %s", TASK)
        celery.send_task(TASK, args=[file_path])


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def main():
    logging.config.dictConfig(settings.LOGGING)
    server = ThreadedTCPServer(
        (settings.HOST, settings.PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    logger.info("Server listening on %s:%d.", ip, port)
    server.serve_forever()  # Interrupt with Ctrl-C.

if __name__ == "__main__":
    main()
