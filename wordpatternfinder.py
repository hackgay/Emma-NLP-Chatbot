import logging

import misc

class InterrogativePackage:
    """
    Packages the important bits of question nicely

    Class variables:
    questionType    str     Type of question ('what is', 'do X have Y', etc.)
    attribute       Word    Half of the important question bits ('what is the color of the sky?' <- 'color')
    subject         Word    The other half ('what is the color of the sky?' <- 'sky')
    """

    def __init__(self, questionType, attribute, subject):
        self.questionType = questionType
        self.attribute = attribute
        self.subject = subject

def package_interrogatives(sentence):
    """Packages questions in a way that's easy to unpack for answering later"""
    # "What is...?"
    if sentence.words[0].lemma == u'what':
        if sentence.words[1].lemma == u'be':
            # Find the attribute and object
            attribute = None
            subject = None
            for word in sentence.words[2:]:
                if word.partOfSpeech i