
    .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\n   d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b\n   888ooo888  888   888   888   888   888   888   .oP"888\n   888    .,  888   888   888   888   888   888  d8(  888\n   `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o\n\n           ELECTRONIC MODEL of MAPPED ASSOCIATIONS\n\n     This is the new home of Emma, originally developed by its creators.\n\nEmma is a computer program that conceptualises associations from inputs. Emma is an unique type of bot that uses these associations to generate replies. Communicate with Emma using Tumblr Asks at [@emma@botsin.space](https://botsin.space/@emma).\n\n## How Does Emma Work? \n1. Emma reads a message from Mastodon \n  - The message is prepared to be read, which involves screening for banned words or vulgar language, as well as expanding common abbreviations and adding punctuation if none exists \n  - The positive or negative sentiment of the message is recorded and used along with other sentiments from other messages to calculate Emma's mood \n  - The message Emma has chosen to respond to is parsed using pattern.en \n    - This gives us all kinds of information about the language used, including lemata, chunks, chunk relations, and parts of speech \n  - We look through the new metadata-tagged sentences to fix up any remaining things that could hinder Emma's understanding\n  - Emma reads through the sentences and records any new words she finds, along with their parts of speech and an affinity score \n  - Emma uses a pattern matching strategy to find key phrase structures in the message that indicate a relationship between two objects, and records the objects and their relationship \n2. Emma replies to the message and posts the response to Mastodon. \n  - Emma looks for important words in the message to determine its context. \n  - Emma decides the number and types of sentences to generate based on the types of associations that exist for a given object. \n  - Emma creates rough outlines of the sentences,  and finally the reply is posted to Mastodon. \n\n## Contact the New Owner\nI'm [@hackgay](http://github.com/hackgay) on Github, feel free to ask me about this project! \n\n## Special Thanks\n * Omri Barak\n * Alexander Lozada 