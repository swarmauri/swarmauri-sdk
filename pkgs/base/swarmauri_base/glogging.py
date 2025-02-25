import logging

# ANSI escape codes for Neon Vibes colors
ANSI_BOLD_BLUE = "\033[1;34m"    # Bold Blue for DEBUG
ANSI_BOLD_GREEN = "\033[1;32m"   # Bold Green for INFO
ANSI_BOLD_YELLOW = "\033[1;33m"  # Bold Yellow for WARNING
ANSI_BOLD_RED = "\033[1;31m"     # Bold Red for ERROR
ANSI_BOLD_MAGENTA = "\033[1;35m" # Bold Magenta for CRITICAL
ANSI_RESET = "\033[0m"           # Reset to default

class NeonVibesFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: ANSI_BOLD_BLUE,
        logging.INFO: ANSI_BOLD_GREEN,
        logging.WARNING: ANSI_BOLD_YELLOW,
        logging.ERROR: ANSI_BOLD_RED,
        logging.CRITICAL: ANSI_BOLD_MAGENTA,
    }
    
    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, ANSI_RESET)
        message = super().format(record)
        return f"{color}{message}{ANSI_RESET}"


glogger = logging.getLogger("GLOG")
glogger.setLevel(level=logging.INFO)
glogger.propagate = False
if not glogger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    glogger.addHandler(console_handler)