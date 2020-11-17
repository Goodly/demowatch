# Create a class for TUAs

class Tua(object):
    """Text units for newspaper article."""

    def __init__(self, start, end, text, tua_type):
        """
        int start: start index of this TUA in its respective news article
        int end: end index of this TUA in its respective news article
        str text: text of this TUA
        param article: article object to associate with this TUA
        """
        # TODO: Can we feed a link into this instead of these individual arguments?
        self.index = [start, end]
        self.text = text
        self.type = tua_type
        self.targets = []

    def set_article(self, article):
        """
        Assign the TUA to the article it's from.
        param article: article object to associate with this TUA
        """
        self.article = article

    def get_text(self):
        """
        str return: text of this TUA
        """
        return self.text

    def get_indices(self):
        """
        list return: start and end indices of this TUA in its respective news article
        """
        return self.index

    def get_article(self):
        """
        article return: article object associated with this TUA
        """
        return self.article

    def add_target(self, target):
        """
        param target: target text objects found in this TUA
        """
        self.targets.append(target)

    def get_targets(self):
        """
        list return: target text objects in this file
        """
        return self.targets