
import argparse
import configparser
import sys
import os
import ssl
import logging
import logging.config
from logging.handlers import SysLogHandler
from logging import FileHandler
from werkzeug.middleware.shared_data import SharedDataMiddleware

from SSearchServer import SSearchServer

logger    = logging.getLogger("SSearch.App")
# handler = SysLogHandler('/dev/log') 
handler   = FileHandler('SSearchServer.log')
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s - [%(module)s] - %(filename)s:%(lineno)d - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def create_app(config="", host="localhost", port=5000, with_static=True):
    # app = SSearchServer({"config": config, "host": host, "port": port})
    app = SSearchServer()
    if with_static:
        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app, {"/static": os.path.join(os.path.dirname(__file__), "static")}
        )
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Semantic Search Server')
    parser.add_argument('-c', '--config', metavar='<config file>', help='Config file', required=False)
    parser.add_argument('-d','--debug', action='store_true', help='Enable Debug', required=False)
    # params = parser.parse_args()

    # configParser       = configparser.ConfigParser()
    # configParser.read(params.config)
    # hostname     = configParser.get('Server', 'hostname')
    # port         = int(configParser.get('Server', 'port'))
    # app_key      = configParser.get('Certs', 'app_key')
    # app_cert     = configParser.get('Certs', 'app_cert')
    # ca_cert      = configParser.get('Certs', 'ca_cert')

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    # if params.debug is True:
    #     # print(loggers)
    #     for logger in loggers:
    #         logger.setLevel(logging.DEBUG)
    #     logger.debug("********* Set all loggers to DEBUG **********")

    from werkzeug.serving import run_simple
    logger.info("Starting main...")

    # app_key = './certs/server/server.key'
    app_key_password = None
    # app_cert = './certs/server/server.crt'
    # ca_cert = './certs/ca/ca-crt.pem'

    # context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_cert )
    # context.check_hostname = False
    # context.hostname_checks_common_name = False
    # context.load_verify_locations(ca_cert)

    # context.load_cert_chain( certfile=app_cert, keyfile=app_key, password=app_key_password )
    # context.verify_mode = ssl.CERT_REQUIRED
    # app = create_app("params.config")
    app = create_app()

    run_simple("localhost", 5000, app, use_debugger=True, use_reloader=True)
    # run_simple(hostname, port, app, use_debugger=False, use_reloader=True, ssl_context=context )
