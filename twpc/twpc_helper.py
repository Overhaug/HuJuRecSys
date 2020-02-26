from bs4 import BeautifulSoup


# A utility class for twpc.py
class TWPCHelper:
    def __init__(self, source_path, save_path, mode=None, batch_size=None, unwanted_properties=None):
        self.mode = mode if mode in ("html", "plain") else "plain"
        self.batch_size = 10000 if batch_size is None else batch_size
        self.unwanted_properties = ("source", "published_date") if unwanted_properties is None else unwanted_properties
        self.source_path = source_path
        self.save_path = save_path + "_" + self.mode + ".csv"
        self.parser = self.get_parser()

    def get_parser(self):
        if self.mode == 'html':
            return self.parse_as_html
        if self.mode == 'plain':
            return self.parse_as_plain

    @staticmethod
    def parse_as_html(text):
        soup = BeautifulSoup(text, "html.parser")
        if soup.text.isspace() or soup.text == '':
            return ''
        return soup.text + " <br><br>"

    @staticmethod
    def parse_as_plain(text):
        soup = BeautifulSoup(text, "html.parser")
        if soup.text.isspace() or soup.text == '':
            return ''
        return soup.text
