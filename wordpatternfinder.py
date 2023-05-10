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
        self.questionType = ques