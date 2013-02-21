import os

SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))

SOCKS = {
    'host': '10.10.101.118',  # socket server host
    'port': 5008,
    'time_per_csv': 60,  # every 1 minute forms a csv file
    'socket_dst': '/home/shaoqing/testdata/socket/',
    'db_name': 'ddsc',  # PostgreSQL DB information
    'db_user': '',
    'db_password': '',
    'db_ip': '10.10.101.118',
}

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BUILDOUT_DIR, 'var', 'log', 'socks.log'),
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

try:
    # Allow each environment to override these settings.
    from ddsc_socket.localsettings import *  # NOQA
except ImportError:
    pass
