
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
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, affinity DOUBLE)
        """)
    logging.debug("Association model created.")

# Set up SQL
connection = sql.connect('emma.db')
connection.text_factory = str
cursor = connection.cursor()

# Dumb chrome
print u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' \u006088b \u0060888P\"Y88bP\"Y88b  \u0060888P\"Y88bP\"Y88b  \u0060P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n\u0060Y8bod8P' o888o o888o o888o o888o o888o o888o \u0060Y888\"\"8o\n\n        ELECTRONIC MODEL of MAPPED ASSOCIATIONS\n                     Version " + misc.versionNumber + "\n"
with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print "Database contains {0} associations for {1} words.".format(associationModelItems, dictionaryItems)

# Check for and load the file containing the history of mood values or create it if it isn't there
logging.info("Loading mood history...")
if os.path.isfile('moodHistory.p'):
    logging.debug("Mood history found!")
    with open('moodHistory.p','rb') as moodFile: moodHistory = pickle.load(moodFile)
    logging.debug("Mood history loaded!")