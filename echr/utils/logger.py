import logging
import os
from rich.logging import RichHandler

from echr.utils.config import config


def setup_console(console):
    global print
    print = console.print


def get_log_folder():
    return config().get('logging', {}).get('log_folder')


def getlogger(logfile_path=None):
    if logfile_path is None:
        log_folder = config().get('logging', {}).get('log_folder')
        log_file = config().get('logging', {}).get('build_log_file')
        logfile_path = os.path.join(log_folder, log_file)

    fh = logging.FileHandler(logfile_path)
    fh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(message)s'))
    fh.setLevel(level="NOTSET")
    rh = RichHandler(show_time=False, show_level=False, show_path=False)
    rh.setLevel(level="ERROR")
    #logging.basicConfig(level="NOTSET", format='%(message)s')
    log = logging.getLogger()
    log.addHandler(fh)
    #log.addHandler(rh)
    return log


def serialize_console_logs(console, filename, path, clear=False):
    console.save_text(os.path.join(path, '{}.txt'.format(filename)), clear=False)
    console.save_html(os.path.join(path, '{}.html'.format(filename)), clear=clear)
