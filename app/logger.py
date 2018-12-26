import logging
from logging.handlers import SysLogHandler

# Logging environment that can be used by the application to output syslog
logging_object = logging.getLogger(__name__)
logging_object.setLevel(logging.INFO)
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
logging_object.addHandler(syslog_handler)
