
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
else:   
    logging.warn("Mood history file not found! Creating...")
    with open('moodHistory.p','wb') as moodFile:
        moodHistory = [0.0] * 10
        pickle.dump(moodHistory, moodFile)
    logging.debug("Mood history file created.")

# Mood-related things
def add_mood_value(text):
    """Adds the new mood value to the front of the history list and removes the last one"""
    moodValue = pattern.en.sentiment(text)[0]
    logging.debug("Adding mood value {0} to mood history {1}...".format(moodValue, moodHistory))
    moodHistory.insert(0, moodValue)
    del moodHistory[-1]
    logging.debug("New mood history is {0}".format(moodHistory))

    # And save!
    logging.debug("Saving mood history...")
    with open('moodHistory.p', 'wb') as moodFile: 
        pickle.dump(moodHistory, moodFile)

    return moodValue

def calculate_mood():
    """Mood is calculated with a weighted mean average formula, skewed towards more recent moods"""
    logging.debug("Calculating mood...")
    # First, we calculate the weighted mood history
    weightedMoodHistory = []
    weightedMoodHistory.extend([moodHistory[0], moodHistory[0], moodHistory[0], moodHistory[1], moodHistory[1]])
    weightedMoodHistory.extend(moodHistory[2:9])

    # And take the average to get the mood
    mood = sum(weightedMoodHistory) / 13
    logging.debug("Mood: {0}".format(mood))
    return mood

def express_mood(moodValue):
    """Returns a string which can be attached to a post as a tag expressing Emma's mood"""
    logging.debug("Expressing mood...")
    if -0.8 > moodValue: 
        return u"feeling abysmal \ud83d\ude31"
    elif -0.6 > moodValue >= -0.8: 
        return u"feeling dreadful \ud83d\ude16"
    elif -0.4 > moodValue >= -0.6: 
        return u"feeling bad \ud83d\ude23"
    elif -0.2 > moodValue >= -0.4: 
        return u"feeling crummy \ud83d\ude41"
    elif 0.0 > moodValue >= -0.2: 
        return u"feeling blah \ud83d\ude15"
    elif 0.2 > moodValue >= 0.0: 
        return u"feeling alright \ud83d\ude10"
    elif 0.4 > moodValue >= 0.2: 
        return u"feeling good \ud83d\ude42"