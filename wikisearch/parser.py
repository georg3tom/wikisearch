import xml.sax as sax
from .page import Page
from .utils.logger import logger
from .preprocess import Preprocess


class WikiParser:
    def __init__(self) -> None:
        self._parser = sax.make_parser()
        self._parser.setFeature(sax.handler.feature_namespaces, 0)

    def parse(self, conf, callback):
        handler = WikiHandler()
        handler.indexCallback(callback)
        self._parser.setContentHandler(handler)
        logger.info("Parsing wiki dump file: {}".format(conf.file))
        self._parser.parse(conf.file)


class WikiHandler(sax.handler.ContentHandler):
    def __init__(self) -> None:
        self._title = []
        self._data = []
        self._id = None
        self._item_tag = "page"
        self._indexer = None
        self._notvalid = True
        self._pre = Preprocess()

    def indexCallback(self, func):
        self._indexer = func

    def startElement(self, tag, _):
        self._tag = tag
        if tag == self._item_tag:
            self._notvalid = False

    def _preprocess(self):
        return self._pre(self._title, self._data)

    def endElement(self, tag):
        if self._item_tag != tag:
            return

        self._title = "".join(self._title)
        self._data = "".join(self._data)
        self._indexer(self._preprocess())
        self._notvalid = True
        self._title = []
        self._data = []
        self._id = None

    def characters(self, content):
        if self._notvalid:
            return
        if self._tag == "title":
            self._title.append(content)
        elif self._tag == "text":
            self._data.append(content)
