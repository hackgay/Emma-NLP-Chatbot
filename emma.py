
# -*- coding: utf-8 -*-
import random
import pickle
import logging
import os
import re
import cgi
import time

import pattern.en
import pattern.vector
import sqlite3 as sql
from mastodon import Mastodon, StreamListener

import flags
import pronouns
import wordpatternfinder
import associationtrainer
import replybuilder
import misc
import apikeys

# Setup stuff
# Set up logging level (this should go in misc.py but eh)
logging.root.setLevel(logging.INFO)

# Pre-flight engine checks
# Check for emma.db or create it if it isn't there
logging.info("Checking for association model")
if os.path.isfile('emma.db'):
    logging.debug("Association model found!")
else:
    logging.warn("Association model not found! Creating")
    with sql.connect('emma.db') as connection:
        connection.cursor().executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;