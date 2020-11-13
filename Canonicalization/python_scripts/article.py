# Create a class for articles
import util

class Article(object):
    """Newspaper article describing an event."""
    def __init__(self, path):
        """
        str path: path to the folder containing the files relevant to this article
        """
        self.path = path
        extract_info()

    def extract_info():
        """
        Sets the data in the files at the filepath to instance attributes.
        """
        self.text = set_text()
        self.id = set_id()
        set_date()
        self.periodical = set_periodical()
        self.city, self.state = set_location()
        self.tuas = set_tuas()

    def set_id():
        pass

    def set_text():
        pass

    def set_date():
        self.article_date = set_article_date()
        self.event_date = set_event_date()

    def set_article_date():
        pass

    def set_event_date():
        """
        Gets the date of the event described in the article.
        param article: article object to get date for
        str return: date of event
        """
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        article_day = util.day_from_date(self.article_date)
        event_day = util.event_day(self.text)
        if not event_day:
            # TODO: extract date if no day mentioned
        difference = (article_day - event_day) mod 7
        self.event_date = util.date_diff(self.article_date, difference)

    def set_periodical():
        pass

    def set_location():
        pass

    def set_tuas():
        pass