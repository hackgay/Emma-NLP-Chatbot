import numpy as np
import re

import sqlite3 as sql

import logging
import misc

E = np.exp(1)
RANKING_CONSTANT = 3.19722457734
def calculate_new_weight(currentWeight):
    """Take an association's weight and increase it"""
    # TODO: This function should be able to de