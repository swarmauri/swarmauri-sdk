import logging

glogger = logging.getLogger("GLOG")
glogger.setLevel(level=logging.INFO)
glogger.propagate = False
if not glogger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    glogger.addHandler(console_handler)