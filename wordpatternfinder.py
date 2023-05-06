import logging

import misc

class InterrogativePackage:
    """
    Packages the important bits of question nicely

    Class variables:
    questionType    str     Type of question ('what is', 'do X have Y', etc.)
    attribute       Word    Half of the important question bits ('what is the c