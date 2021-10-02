from .page import Page
import re
from .utils.logger import logger
from Stemmer import Stemmer


class Preprocess:
    def __init__(self):
        self.infobox = re.compile(r"{{(?:i|I)nfobox(?:[^}])*}}")
        self.links = re.compile(r"\[http.?://(?:[^\s])*((?:.)*)\]")
        self.links_r = re.compile(r"\[http.?://(?:.)*\]")
        self.categories = re.compile(r"\[\[Category:(.*)\]\]")
        self.categories_r = re.compile(r"\[\[Category:.*\]\]")
        self.references = re.compile(r"{{cite(.*)}}")
        self.references_r = re.compile(r"{{cite.*}}")
        with open("./cache/english", "r") as f:
            self.stopwords_init = f.read().splitlines()
        self.waste = [
            re.compile(r"http.?://(?:[^\s])*"),  # urls
            re.compile(r"(\|[^\|\n\]]*=)"),  # | * =
            re.compile(r"#[0-9a-fA-F]+"),  # hex colors
            re.compile(r"&(?:[^;])*;!?"),  # &**;
            re.compile(r"[^a-z'\s0-9]"),  # non alpha num
            # re.compile(r"\b\w{1,2}\b"),  # word len < 2
            re.compile(r"\b[0-9]+[a-z]+\b"),  # word nums
            re.compile(r"\b[a-z]+[0-9]+\b"),  # word nums
            re.compile(r"\b[\d]{7,}\b"),  # numbers > 7
        ]
        self.stopwords = re.compile(r"\b(" + r"|".join(self.stopwords_init) + r")\b\s*")
        self.apostrophe = re.compile(r"'")
        self.stemmer = Stemmer("english")
        self.stemmer.maxCacheSize = 1000000
        self._doc_id = 1

    def __call__(self, title, data):
        return self._preprocess(title, data)

    def _preprocess(self, title, data) -> Page:
        page = Page()
        page.id = self._doc_id
        page.title_orginal = title.lower()
        self._doc_id += 1
        page.title = [title]
        page.infobox = self.infobox.findall(data)
        data = self.infobox.sub("", data)
        page.categories = self.categories.findall(data)
        data = self.categories_r.sub("", data)
        page.links = self.links.findall(data)
        data = self.links_r.sub("", data)
        page.references = self.references_r.findall(data)
        page.body = [data]
        return self.preprocess_page(page)

    def preprocess_page(self, page) -> Page:
        page = self._clean(page)
        page = self._tokenise(page)
        return page

    def _clean(self, page: Page):
        page.apply(str)
        page.apply(str.lower)

        def strip(s):
            return " ".join(s.split())

        def remove_waste(s):
            for waste in self.waste:
                s = waste.sub(" ", s)
            s = self.apostrophe.sub("", s)
            return s

        def remove_stopwords(s):
            s = self.stopwords.sub("", s)
            return s

        page.infobox = [" ".join(page.infobox)]
        page.categories = [" ".join(page.categories)]
        page.references = [" ".join(page.references)]
        page.links = [" ".join(page.links)]
        page.apply(remove_waste)
        page.apply(strip)
        page.apply(remove_stopwords)
        page.apply(strip)
        return page

    def _tokenise(self, page):
        page.apply(str.split)

        def return_inner(l):
            if len(l) == 0:
                return l
            return l[0]

        page.apply_list(return_inner)
        page.apply_list(self.stemmer.stemWords)
        return page
