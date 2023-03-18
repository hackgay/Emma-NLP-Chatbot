
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
            self.partOfSpeech = SQLReturn[0]

class SBBHaveHas:
    def __init__(self):
        pass

class SBBIsAre:
    def __init__(self):
        pass

class SBBArticle:
    def __init__(self):
        pass

class SBBConjunction:
    def __init__(self):
        pass

class SBBPunctuation:
    def __init__(self):
        pass

def weighted_roll(choices):
    """Takes a list of (weight, option) tuples and makes a weighted die roll"""
    dieSeed = 0
    for choice in choices:
        dieSeed += choice[0]
    dieResult = random.uniform(0, dieSeed)

    for choice in choices:
        dieResult -= choice[0]
        if dieResult <= 0:
            return choice[1]

class Association:
    def __init__(self, word, associationType, target, weight):
        self.word = word
        self.target = target
        self.associationType = associationType
        self.weight = weight

def find_associations(keyword):
    """Finds associations in our association model for given keywords"""
    logging.debug("Finding associations for {0}...".format(keyword)) 
    associations = []
    with connection:
        cursor.execute('SELECT * FROM associationmodel WHERE word = ? OR target = ?;', (keyword, keyword))
        SQLReturn = cursor.fetchall()
        for row in SQLReturn:
            associations.append(Association(row[0], row[1], row[2], row[3]))
    return associations

def find_part_of_speech(keyword):
    """Looks in our dictionary for the part of speech of a given keyword"""
    # TODO: Make this able to handle words with more than one usage
    logging.debug("Looking up \"{0}\" in the dictionary...".format(keyword))
    with connection:
        cursor.execute('SELECT part_of_speech FROM dictionary WHERE word = ?;', (keyword,))
        SQLReturn = cursor.fetchall()
        if SQLReturn:
            return SQLReturn[0]
        else:
            return "NN"

# TODO: Random choices should be influenced by mood or other
def make_declarative(sentence):
    # Look for HAS, IS-A or HAS-ABILITY-TO associations 
    associations = find_associations(sentence.topic)
    hasAssociations = []
    isaAssociations = []
    hasabilitytoAssociations = []
    haspropertyAssociations = []
    for association in associations:
        if association.associationType == "HAS" and association.word == sentence.topic:
            hasAssociations.append((association.weight, association))
        elif association.associationType == "IS-A" and association.word == sentence.topic:
            isaAssociations.append((association.weight, association))
        elif association.associationType == "HAS-ABILITY-TO" and association.word == sentence.topic:
            hasabilitytoAssociations.append((association.weight, association))
        elif association.associationType == "HAS-PROPERTY" and association.word == sentence.topic:
            haspropertyAssociations.append((association.weight, association))
            
    # If we have associations other than HAS-PROPERTY ones, we can make more complex sentences
    allowComplexDeclarative = False
    if len(hasAssociations) > 0 or len(isaAssociations) or len(hasabilitytoAssociations) > 0:
        allowComplexDeclarative = True

    # Decide what kind of sentence to make and make it
    if random.choice([False, allowComplexDeclarative]):
        # Complex
        # Decide /what kinds/ of complex sentence we can make
        validSentenceAspects = []
        if len(hasAssociations) > 0:
            validSentenceAspects.append('HAS')
        if len(isaAssociations) > 0:
            validSentenceAspects.append('IS-A')
        if len(hasabilitytoAssociations) > 0:
            validSentenceAspects.append('HAS-ABILITY-TO')
        # Choose the kind of sentence to make
        sentenceAspect = random.choice(validSentenceAspects)

        if sentenceAspect == 'HAS':
            sentence = make_simple(sentence)
            sentence.contents.append(SBBHaveHas())
            if random.choice([True, False]):
                sentence.contents.append(SBBArticle())
                sentence.contents.append(weighted_roll(hasAssociations).target)
            else:
                sentence.contents.append(pattern.en.pluralize(weighted_roll(hasAssociations).target))
        elif sentenceAspect == 'IS-A':
            sentence = make_simple(sentence)
            sentence.contents.extend([SBBIsAre(), SBBArticle()])
            sentence.contents.append(weighted_roll(isaAssociations).target)
        elif sentenceAspect == 'HAS-ABILITY-TO':
            if random.choice([True, False]):
                sentence = make_simple(sentence)
                sentence.contents.append(u'can')
                sentence.contents.append(weighted_roll(hasabilitytoAssociations).target)
            else:
                sentence = make_simple(sentence)
                sentence.contents.append(pattern.en.conjugate(weighted_roll(hasabilitytoAssociations).target, number="PL"))
    else:
        # Simple
        if random.choice([True, False]):
            sentence = make_simple(sentence)
        else:
            sentence.contents.append(sentence.topic)
        sentence.contents.append(SBBIsAre())
        sentence.contents.append(weighted_roll(haspropertyAssociations).target)
        
    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_imperative(sentence):
    # Look for things the object can do
    associations = find_associations(sentence.topic)

    # Get HAS-ABILITY-TO associations and also look for HAS associations
    hasabilitytoAssociations = []
    hasAssociations = []
    for association in associations:
        if association.associationType == "HAS-ABILITY-TO" and association.word == sentence.topic:
            hasabilitytoAssociations.append((association.weight, association))
        elif association.associationType == "HAS" and association.word == sentence.topic:
            hasAssociations.append((association.weight, association))

    # If we have HAS associations, we can make slightly more complex sentences
    allowComplexImperative = False
    if len(hasAssociations) > 0:
        allowComplexImperative = True

    # Make the sentence
    sentence.contents.append(sentence.topic)
    if random.choice([True, False]):
        sentence.contents.append(u'can')
    # Coin Flip to decide whether to add always or never
    if random.choice([True, False]):
        sentence.contents.append(random.choice([u'always', u'never', u'sometimes']))
    sentence.contents.append(weighted_roll(hasabilitytoAssociations).target)
    if random.choice([False, allowComplexImperative]):
        # if random.choice([True, False]):
        #     sentence.contents.append(u'with')
        if random.choice([True, False]):
            sentence.contents.append(SBBArticle())
            sentence.contents.append(weighted_roll(hasAssociations).target)
        else:
            if sentence.isPlural:
                sentence.contents.append(pattern.en.pluralize(weighted_roll(hasAssociations).target))
            else:
                sentence.contents.append(weighted_roll(hasAssociations).target)
        
    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_interrogative(sentence):
    # Start the setence with a template
    starters = [
        [u'what', u'is'],
        [u'what\'s'],
        [],
    ]
    sentence.contents.extend(random.choice(starters))

    # Add on the subject
    sentence = make_simple(sentence)

    sentence.contents.append(u'?')
    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_simple(sentence):
    # Look for adjectives to describe the object
    associations = find_associations(sentence.topic)

    # Decide whether to add an article
    if random.choice([True, False]):
        sentence.contents.append(SBBArticle())

    # See if we have any adjective associations handy
    haspropertyAssociations = []
    for association in associations:
        if association.associationType == "HAS-PROPERTY" and association.word == sentence.topic:
            haspropertyAssociations.append((association.weight, association))