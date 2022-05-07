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
                with connection:
                    cursor.execute('UPDATE associationmodel SET weight = ? WHERE word = ? AND association_type = ? AND target = ?;', (weight, word.encode('utf-8', 'ignore'), associationType, target.encode('utf-8', 'ignore')))
                logging.info("Strengthened association \"{0} {1} {2}\"".format(word.encode('utf-8', 'ignore'), associationType, target.encode('utf-8', 'ignore')))
            else:
                # Association does not exist, so add it
                # This is the weight calculated for all new associations
                weight = 0.0999999999997
                with connection:
                    cursor.execute('INSERT INTO associationmodel(word, association_type, target, weight) VALUES (?, ?, ?, ?);', (word.encode('utf-8', 'ignore'), associationType, target.encode('utf-8', 'ignore'), weight))
                logging.info("Found new association \"{0} {1} {2}\"".format(word.encode('utf-8', 'ignore'), associationType, target.encode('utf-8', 'ignore')))

def find_associations(message):
    """Use pattern recognition to learn from a Message object"""
    for sentence in message.sentences:
        # We don't want to learn from questions
        if sentence.sentence[-1] != u'?':
            for word in sentence.words:
                # Don't associate parts of speech we can't actually use
                if word.partOfSpeech not in misc.trashPOS:
                    # Check for words behind the word we're on
                    if sentence.length - word.index > 0:
                        # Check for words in front of the word we're on
                        if sentence.length != word.index + 1:
                            # Look for keywords
                            if word.lemma == u'be' or word.lemma == u'mean':
                                if "NP" in sentence.words[word.index-1].chunk:
                                    if "ADJP" in sentence.words[word.index+1].chunk or "NP" in sentence.words[word.index+1].chunk:
                                        for nextWord in sentence.words[word.index+1:-1]:
                                            # NP + 'be' + ADJP >> NN HAS-PROPERTY JJ (milk is white >> milk HAS-PROPERTY white)
                                            if nextWord.partOfSpeech in misc.adjectiveCodes:
                                                train_association(sentence.words[word.index-1].lemma, 'HAS-PROPERTY', nextWord.lemma)

                                            # NP + 'be' + NP >> NN IS-A NN (a dog is an animal >> dog IS-A animal)
                                            elif nextWord.partOfSpeech in misc.nounCodes:
                                                train_association(sentence.words[word.index-1].lemma, "IS-A", nextWord.lemma)
                                                # A noun should be the last word in this pattern, so
                                                break

                                            elif "NP" in nextWord.chunk or nextWord.lemma == u'and': 
                                                continue
                                            # Catch us if we go too far because of incorrect sentence parsing
                                            else:
                                                break
                            if "NP" in word.chunk and word.partOfSpeech in misc.nounCodes:
                                # NP containing JJ + NN >> NN HAS-PROPERTY JJ (the big house >> house HAS-PROPERTY big)
                                for adjectiveCandidate in reversed(sentence.words[0:word.index]):
                                    if adjectiveCandidate.partOfSpeech in misc.adjectiveCodes:
                        