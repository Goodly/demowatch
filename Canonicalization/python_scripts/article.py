# Create a class for articles
import util

class Article(object):
    """Newspaper article describing an event."""
    def __init__(self, path):
        """
        str path: path to the folder containing the files relevant to this article
        """
        self.path = path
        self.tuas = []
        util.convert_gzip(self.path)
        extract_info()

    def extract_info():
        """
        Sets the data in the files at the filepath to instance attributes.
        """
        metadata = eval(open(self.path + "metadata.json").read())
        self.text = open(self.path + 'text.txt', 'r').read()
        self.id = metadata["filename"].split(".")[0]
        self.article_date = metadata["date_published"]
        self.event_date = set_event_date()
        self.city, self.periodical = metadata["city"].split("-")
        set_tuas()

    def set_event_date():
        """
        Sets the date of the event described in the article to instance attributes.
        """
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        article_day = util.day_from_date(self.article_date)
        event_day = util.event_day(self.text)
        if event_day:
            difference = (article_day - event_day) mod 7
            if difference == 0:
                difference = 7
            self.event_date = util.date_diff(self.article_date, difference)
        else:
            self.event_date = self.article_date

    def set_tuas():
        """
        Creates and stores TUA objects for each TUA noted in this article
        """
        pass