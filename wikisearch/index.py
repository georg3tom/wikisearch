from .parser import WikiParser
from .page import Page
from pathlib import Path
from .utils.logger import logger
from collections import Counter
from Stemmer import Stemmer
import re


class Index:
    def __init__(self, conf):
        self.config = conf
        self._block_pre = self.config.save + "/b"
        self._block_no = 0
        self._block = self._block_pre + str(self._block_no)
        Path(self.config.save).mkdir(parents=True, exist_ok=True)
        self.max_size = 1000000
        self.dict = {}
        self.tokens_all = set()

    def build(self):
        parser = WikiParser()
        parser.parse(self.config, self.index)
        self._save()
        with open(self.config.stats, "a") as f:
            f.write(str(len(self.tokens_all)))

    def index(self, page: Page):

        unq = set()
        title_c = Counter(page.title)
        unq.update(title_c)
        categories_c = Counter(page.categories)
        unq.update(categories_c)
        body_c = Counter(page.body)
        unq.update(body_c)
        references_c = Counter(page.references)
        unq.update(references_c)
        infobox_c = Counter(page.infobox)
        unq.update(infobox_c)
        links_c = Counter(page.links)
        unq.update(links_c)
        self.tokens_all.update(unq)

        for token in unq:
            counts = [
                title_c[token],
                body_c[token],
                categories_c[token],
                references_c[token],
                infobox_c[token],
                links_c[token],
            ]
            self._add_to_dict(page.id, token, counts)

    def _add_to_dict(self, id, token, counts):
        # if self.max_size < len(self.dict):
        #     self._write_block()

        m = ["t", "b", "c", "r", "i", "l"]
        out = [str(id)]
        for i, count in enumerate(counts):

            if count != 0:
                out.append(m[i])
                out.append(str(count))

        out = "".join(out)

        if token in self.dict:
            self.dict[token].append(out)
        else:
            self.dict[token] = [out]

    def _save(self):
        logger.info("Writing block {}".format(self._block))
        sort_dict = sorted(self.dict)
        with open(self._block, "w") as f:
            for token in sort_dict:
                f.write("{} {}\n".format(token, "-".join(self.dict[token])))
        self._block_no += 1
        self._block = self._block_pre + str(self._block_no)
        self.dict = {}

    def load(self):
        with open(self.config.save + "/b0", "r") as f:
            self.data = f.read().splitlines()

    def search(self):
        self.load()
        get_id = re.compile(r"^[0-9]*")
        query = self.config.query
        query = query.replace("t:", "")
        query = query.replace("b:", "")
        query = query.replace("i:", "")
        query = query.replace("c:", "")
        query = query.replace("r:", "")
        query = query.replace("l:", "")
        query = query.lower()
        with open("./cache/english", "r") as f:
            stopwords = f.read().splitlines()
        query = query.split()
        stemmer = Stemmer("english")
        stem_query = stemmer.stemWords(query)
        query = sorted(query)
        ret = {}
        for i, q in enumerate(query):
            ret[q] = {}
            ret[q]["title"] = []
            ret[q]["body"] = []
            ret[q]["infobox"] = []
            ret[q]["categories"] = []
            ret[q]["references"] = []
            ret[q]["links"] = []
        for line in self.data:
            for i, q in enumerate(query):
                if q in stopwords:
                    continue
                if line.startswith(stem_query[i]):
                    entry = line.split()[1]
                    entry = line.split("-")[1:]
                    for e in entry:
                        id = get_id.findall(e)[0]
                        if "t" in e:
                            ret[q]["title"].append(id)
                        if "b" in e:
                            ret[q]["body"].append(id)
                        if "c" in e:
                            ret[q]["categories"].append(id)
                        if "i" in e:
                            ret[q]["infobox"].append(id)
                        if "r" in e:
                            ret[q]["references"].append(id)
                        if "l" in e:
                            ret[q]["links"].append(id)

        return ret

    def _search_token(self, token):
        pass
