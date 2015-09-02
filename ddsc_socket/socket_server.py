# (c) Fugro GeoServices, Nelen & Schuurmans. MIT licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
import SocketServer
import logging.config
import os

import psycopg2
import pytz

from ddsc_socket import settings
from ddsc_socket.celery import celery

logger = logging.getLogger(__name__)

BUFSIZE = 1024  # bytes
SQL = "SELECT count(1) FROM lizard_nxt_ipmapping WHERE ip_address = '{}';"


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        ip, port = self.client_address
        logger.info("Client connecting from %s:%d.", ip, port)

        try:
            conn, cur = None, None
            conn = psycopg2.connect(**settings.DATABASE)
            cur = conn.cursor()
            cur.execute(SQL.format(ip))
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
            logger.warning("Will not serve %s (unauthorized).", ip)
            return

        self.request.send("ok")
        data = self.request.recv(BUFSIZE)  # BLOCKING

        if not data:
            logger.info("Connection with %s lost.", ip)
            return

        utc = datetime.now(pytz.utc).isoformat()
        filename = "{}_{}.csv".format(ip, utc)
        file_path = os.path.join(settings.DIR, filename)

        # TODO: implement a timeout.
        # TODO: implement a rolling file.

        with open(file_path, 'wb') as f:
            f.write(data)
            while True:
                self.request.send("ok")
                data = self.request.recv(BUFSIZE)  # BLOCKING
                if data:
                    f.write(data)
                else:
                    logger.info("Connection with %s lost.", ip)
                    break

        logger.info("New file to be imported: %s.", file_path)

        celery.send_task(
            "lizard_nxt.tasks.import_socket_timeseries_from_csv",
            kwargs={'file_path': file_path})


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
