#!/usr/bin/env python3
# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
# pylint: disable=C0103
"""
Main DeltaSherlock client module. Uses machine learning to indentify installed
applications in the hope of locating possible vulnerabilities or intrusions. The
client module facilitates the filesystem scanning and fingerprinting process,
while actual identification is performed by a separate server module. Intended
to be run on a fixed schedule (ex. every 2 minutes).
"""

import sys
import argparse
import configparser
import logging
from logging.handlers import SysLogHandler

VERSION = '0.1a'


def init_args():
    """Process command line arguments"""
    parser = argparse.ArgumentParser(description="DeltaSherlock Client software.")
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('-c', '--config', action='store', dest='config_file',
                        default='./config.ini', help="Path to config file. [default: \
                                                      %(default)s]")
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon',
                        default=False, help="Run in daemon mode. [default: \
                                             %(default)s]")
    return parser.parse_args()


def init_config(filename):
    """Read specified configuration INI file"""
    config = configparser.ConfigParser()
    try:
        with open(filename, 'r') as config_file:
            config.read(config_file)
    except EnvironmentError:
        print("FATAL ERROR: Failed to open config file at " + filename)
        sys.exit(1)
    return config


def parse_log_level(x):
    """Identify log level in config file"""
    return {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }.get(x, None)


def init_logging(location, level):
    """Initialize logging functions"""
    if location is None:
        # Disable Logging (Quiet Mode)
        logging.getLogger().disabled = True
    elif location is "syslog":
        # Log to Syslog
        syslog = SysLogHandler(address='/dev/log')
        if sys.platform is 'darwin':
            # Hack for macOS
            syslog = SysLogHandler(address='/var/run/syslog')
        logging.basicConfig(level=level, handlers=[syslog])
    else:
        # Log to specified file
        logging.basicConfig(level=level, filename=location)

    logger = logging.getLogger(__name__)
    logger.info("DeltaSherlock Version %s", VERSION)
    logger.debug("Logger initialized: %s", str(logger))
    return logger


def main():
    """Main method. Runs on application execution"""
    # Initialization
    args = init_args()
    config = init_config(args.config_file)
    logger = init_logging(location=config['main']['log_location'],
                          level=parse_log_level(config['main']['log_level']))


# Standard boilerplate to call the main() function to begin the program.
if __name__ == '__main__':
    main()
