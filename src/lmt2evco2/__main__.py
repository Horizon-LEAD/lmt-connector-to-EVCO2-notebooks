"""Main Entrypoint module

Based on argparse
"""

import logging
from logging.handlers import RotatingFileHandler
from os.path import isfile, join, exists
from sys import argv
from datetime import datetime
from argparse import (ArgumentParser, RawTextHelpFormatter,
                      ArgumentDefaultsHelpFormatter, ArgumentTypeError)

from .proc import run_model


LOG_FILE_MAX_BYTES = 50e6
LOG_MSG_FMT = "%(asctime)s %(levelname)-8s %(name)s \
%(filename)s#L%(lineno)d %(message)s"
LOG_DT_FMT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("lmt2evco2")


class RawDefaultsHelpFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    """Argparse formatter class"""


def strfile(path):
    """Argparse type checking method
    string path for file should exist"""
    if isfile(path):
        return path
    raise ArgumentTypeError("Input file does not exist")


def strdir(path):
    """Argparse type checking method
    string path for file should exist"""
    if exists(path):
        return path
    raise ArgumentTypeError("Input directory does not exist")

def date(input):
    """Argparse type checking method
    string path for file should exist"""
    try:
        _ = datetime.strptime(input, "%Y-%m-%d")
        return input
    except ValueError:
        raise ArgumentTypeError("Input dates do not conform with format YYYY-mm-dd")


def get_log_level(vcount):
    """Translates the CLI input of the user for the verbosity
    to an actual logging level.

    :param vcount: The user input in verbosity counts
    :type vcount: int
    :return: The logging level constant
    :rtype: int
    """
    loglevel = logging.ERROR
    if vcount >= 3:
        loglevel = logging.DEBUG
    elif vcount == 2:
        loglevel = logging.INFO
    elif vcount == 1:
        loglevel = logging.WARNING
    else:
        return loglevel

    return loglevel


def main():
    """Main method.
    """

    # command line argument parsing
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDefaultsHelpFormatter)

    parser.add_argument('lmt_json', type=strfile,
                        help='The path of the input JSON file as returned by LMT model')
    parser.add_argument('factors_xlsx', type=strfile,
                        help='The path of the input XLSX file with factors')
    parser.add_argument('from_date', type=date,
                        help='The from-date to get the energy production')
    parser.add_argument('to_date', type=date,
                        help='The to-date to get the energy production')
    parser.add_argument('out_dir', type=strdir, help='The output directory')

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')
    parser.add_argument('--flog', action='store_true', default=False,
                        help='Stores logs to file')
    args = parser.parse_args(argv[1:])

    # setting of the logger
    formatter = logging.Formatter(fmt=LOG_MSG_FMT, datefmt=LOG_DT_FMT)
    shandler = logging.StreamHandler()
    shandler.setFormatter(formatter)
    logger.addHandler(shandler)
    if args.flog:
        fhandler = RotatingFileHandler(
            join(args.out_dir, "logs.txt"),
            mode='w',
            backupCount=1,
            maxBytes=LOG_FILE_MAX_BYTES
        )
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)

    loglevel = get_log_level(args.verbosity)
    logger.setLevel(loglevel)

    logger.debug('CMD : %s', ' '.join(argv))
    logger.debug('ARGS: %s', args)

    # setting of the configuration
    run_model(args.lmt_json, args.factors_xlsx,
              args.from_date, args.to_date)


if __name__ == "__main__":
    main()
