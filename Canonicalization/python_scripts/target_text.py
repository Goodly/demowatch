# Create class for target text
# Not usable until we get user data

class Target(object):
    """Target text object answering a question."""
        def __init__(self, tua, start, end, text):
            """
            int start: start index of this target text in its respective news article
            int end: end index of this target text in its respective news article
            str text: target text
            param tua: tua object that this target text is found in
            """
            self.index = [start, end]
            self.text = text
            self.tua = tua

        def get_text():
            """
            str return: target text
            """
            return self.text

        def get_indices():
            """
            list return: start and end indices of target text in its respective news article
            """
            return self.index

        def get_tua():
        	"""
        	param return: TUA object this target text is found in
        	"""
        	return self.tua