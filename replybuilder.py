
import logging
import random
import re
import string

import pattern.en
import sqlite3 as sql

import misc

connection = sql.connect('emma.db')
cursor = connection.cursor()

class Sentence:
    def __init__(self):
        self.domain = ''
        self.topic = ''
        self.isPlural = False
        self.contents = []

class SBBWord:
    def __init__(self, word, partOfSpeech):
        self.word = word
        self.partOfSpeech = str

        with connection:
            cursor.execute('SELECT part_of_speech FROM dictionary WHERE word = ?;', (self.word,))
            SQLReturn = cursor.fetchall()