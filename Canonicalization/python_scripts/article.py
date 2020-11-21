# Create a class for articles
import util
import json
from tua import Tua

class Article(object):
    """Newspaper article describing an event."""
    def __init__(self, path):
        """
        str path: path to the folder containing the files relevant to this article
        """
        self.path = path
        self.tuas = []
        #util.convert_gzip(self.path)
        self.extract_info()

    def extract_info(self):
        """
        Sets the data in the files at the filepath to instance attributes.
        """
        metadata = json.loads(open(self.path + "/metadata.json").read())
        self.text = open(self.path + '/text.txt', 'r').read().split("\n\n")[1]
        self.id = metadata["filename"].split(".")[0]
        self.article_date = metadata["date_published"]
        self.set_event_date()
        self.city, self.periodical = metadata["city"].split("-")
        self.set_tuas()

    def set_event_date(self):
        """
        Sets the date of the event described in the article to instance attributes.
        """
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        article_day = util.day_from_date(self.article_date)
        event_day = util.event_day(self.text)
        if event_day:
            difference = (article_day - event_day) % 7
            if difference == 0:
                difference = 7
            self.event_date = util.date_diff(self.article_date, difference)
        else:
            self.event_date = self.article_date

    def set_tuas(self):
        """
        Creates and stores TUA objects for each TUA noted in this article
        """
        raw_tuas = json.loads(open(self.path + "/annotations.json").read())["tuas"]
        tua_dict = util.flatten_tuas(raw_tuas)
        for tua_type in tua_dict:
            for t in tua_dict[tua_type]:
                text = t[2].replace("[", "").replace("]", "")
                tua = Tua(t[0], t[1], text.strip(), tua_type)
                self.tuas.append(tua)
        for t in self.tuas:
            t.set_article(self)

    def same_event(self, article):
    	"""
    	Check if the given article describes the same event as this article.
    	param article: article to compare this to
    	bool return: whether they're the same event
    	"""
    	return self.event_date == article.event_date and self.city == article.city
