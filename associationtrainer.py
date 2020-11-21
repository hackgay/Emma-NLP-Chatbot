import numpy as np
import re

import sqlite3 as sql

import logging
import misc

E = np.exp(1)
RANKING_CONSTANT = 3.19722457734
def calculate_new_weight(currentWeight):
    """Take an association's weight and increase it"""
    # TODO: This function should be able to decrease weights too
    # Don't let weights be exactly 1 because this breaks stuff
    if currentWeight == 1:
        currentWeight = 0.999999999994
    
    # Transform the weight back into the number of occurances of the word
    occurances = np.log(currentWeight/(1-currentWeight))+RANKING_CONSTANT
    occurances += 1

    # Re-calculate weight
    newWeight = 1/(1+E**(occurances-RANKING_CONSTANT))
    return newWeight

connection = sql.connect('emma.db')
connection.text_factory = str
cursor = connection.cursor()
def train_association(word, associationType, target):
    """Adds an association to the database"""
    # We want to ignore associations with self, so:
    if word != target:
        word = re.escape(word)
        target = re.escape(target)

        # Check to see if the association already exists
        with connection:
            cursor.execute('SELECT * FROM associationmodel WHERE word = ? AND association_type = ? AND target = ?;', (word.encode('utf-8', 'ignore'), associationType, target.encode('utf-8', 'ignore')))
            SQLReturn = cursor.fetchall()
            if SQLReturn:
                # Association already exists, so we strengthen it
                weight = calculate_new_weight(SQLReturn[0][3])
                wit