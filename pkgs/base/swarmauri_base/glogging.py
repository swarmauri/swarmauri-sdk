import logging

glogger = logging.getLogger(__name__)
glogger.setLevel(level=logging.INFO)
glogger.propagate = False
if not glogger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    glogger.addHandler(console_handler)