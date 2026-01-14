from matplotlib.ticker import FuncFormatter
import logging
import sys

def setup_logger(name="AadhaarAnalytics"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def format_indian(x, pos):
    if x >= 10000000:
        return f'{x/10000000:.1f} Cr'
    elif x >= 100000:
        return f'{x/100000:.1f} L'
    else:
        return f'{x:.0f}'

indian_formatter = FuncFormatter(format_indian)
