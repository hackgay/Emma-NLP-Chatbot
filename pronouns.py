
import logging

def determine_pronoun_references(message):
    """Gets a Message object and iterates through sentences/words, replacing pronouns with the last used noun"""
    # Ideally I'd split pronouns into personal pronouns (she/her) and object pronouns (it/its) 
    # so that the nouns that they reference could be tracked seperately
    # but there are people who use it/its and similar pronouns so idk :/
    pronouns = [
        u'he', u'him', u'his', u'himself',
        u'she', u'her', u'hers', u'herself',
        u'they', u'them', u'their', u'theirs', u'themself', u'themselves',
        u'it', u'its', u'itself'
    ]

    logging.debug("Determining pronoun references...")
    lastUsedNoun = None
    for sentence in message.sentences:
        for word in sentence.words:
            # Check if the word is a noun and save it if it is