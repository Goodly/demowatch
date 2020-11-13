# Create a class for TUAs

class Tua(object):
    """Text units for newspaper article."""

        def __init__(self, article, start, end, text, tua_type):
            """
            int start: start index of this TUA in its respective news article
            int end: end index of this TUA in its respective news article
            str text: text of this TUA
            param article: article object to associate with this TUA
            """
            # TODO: Can we feed a link into this instead of these individual arguments?
            self.index = [start, end]
            self.text = text
            self.article = article
            self.type = tua_type

        def get_text():
            """
            str return: text of this TUA
            """
            return self.text

        def get_indices():
            """
            list return: start and end indices of this TUA in its respective news article
            """
            return self.index

        def get_article():
            """
            article return: article object associated with this TUA
            """
            return self.article

        def add_target(target):
            """
            param target: target text objects found in this TUA
            """
            self.targets.append(target)

        def get_targets():
            """
            list return: target text objects in this file
            """
            return self.targets

        # Object representing the article that this TUA comes from
        self.article = None

        # List of target text objects found in this tua
        self.targets = []