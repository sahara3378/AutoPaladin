# coding=gbk
import logging, os
from logging.handlers import TimedRotatingFileHandler
import datetime


path = os.path.join(os.environ.get('AutoPaladin'), 'log', 'paladin-test.{}.log')
logger = logging.getLogger(path)
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
sh.setLevel(logging.DEBUG)
fh = TimedRotatingFileHandler(path.format(datetime.datetime.now().strftime('%Y-%m-%d')),when="D",interval=1,encoding='utf-8')
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.addHandler(fh)


def debug(message):
    logger.debug(message)


def info(message):
    logger.info(message)


def warn(message):
    logger.warning(message)


def error(message):
    logger.error(message)


def cri(message):
    logger.critical(message)
