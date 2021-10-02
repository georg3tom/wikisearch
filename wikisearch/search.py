from .utils.logger import logger
from .preprocess import Preprocess
from .page import Page
from .ranking import BM25
import re
import json
from pathlib import Path
import linecache
import time
from math import sqrt


class Search:
    def __init__(self, conf):
        self.conf = conf
        self.preprocess = Preprocess()
        with open(self.conf.query, "r") as f:
            self.queries = f.read().splitlines()
        with open(self.conf.meta_path, "r") as f:
            self.meta = json.load(f)
        with open(self.conf.token_count, "r") as f:
            self.token_count = f.read().splitlines()

        self._search()

    def _get_filename(self, token):
        for key in self.meta:
            if self.meta[key]["first"] <= token and self.meta[key]["last"] >= token:
                return key

    def _search(self):
        output = open(self.conf.result, "w")
        for query in self.queries:
            logger.info("Querying: {}".format(query))
            page = Page()
            tokens = set()
            start = time.time()

            if "t:" in query:
                page.title = re.findall("t:[^:]+:?", query)[0][2:]
                if ":" in page.title:
                    page.title = page.title[:-2]
                page.title = [page.title]

            if "b:" in query:
                page.body = re.findall("b:[^:]+:?", query)[0][2:]
                if ":" in page.body:
                    page.body = page.body[:-2]
                page.body = [page.body]

            if "i:" in query:
                page.infobox = re.findall("i:[^:]+:?", query)[0][2:]
                if ":" in page.infobox:
                    page.infobox = page.infobox[:-2]
                page.infobox = [page.infobox]

            if "r:" in query:
                page.references = re.findall("r:[^:]+:?", query)[0][2:]
                if ":" in page.references:
                    page.references = page.references[:-2]
                page.references = [page.references]

            if "l:" in query:
                page.links = re.findall("l:[^:]+:?", query)[0][2:]
                if ":" in page.links:
                    page.links = page.links[:-2]
                page.links = [page.links]

            if "c:" in query:
                page.categories = re.findall("c:[^:]+:?", query)[0][2:]
                if ":" in page.categories:
                    page.categories = page.categories[:-2]
                page.categories = [page.categories]

            if ":" not in query:
                page.id = -1
                page.title = [query]
            page = self.preprocess.preprocess_page(page)

            tokens.update(page.title)
            tokens.update(page.body)
            tokens.update(page.infobox)
            tokens.update(page.categories)
            tokens.update(page.references)
            tokens.update(page.links)
            tokens = sorted(tokens)

            doc_tok_freq = {}
            
            for token in tokens:
                file_name = Path(self.conf.save + "/" + self._get_filename(token))
                posting = None
                with open(file_name, "r") as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if line.startswith(token + " "):
                            posting = line.split()[1]
                            break
                if posting is None:
                    continue
                doc_tok_freq = self._update_count_map(
                    doc_tok_freq, token, posting, page
                )
            if doc_tok_freq == {}:
                out = "Doc not found"
                output.write("{}\n".format(out))
                logger.info("{}".format(out))
                output.write("{}\n\n".format(time.time() - start))
                continue

            if len(token) > 2:
                MAX_TOK = int(sqrt(len(tokens)))
                MAX = 50000
                ids = list(doc_tok_freq.keys())
                for id in ids:
                    if doc_tok_freq[id]["token_count"] < MAX_TOK:
                        doc_tok_freq.pop(id, None)
                    if len(doc_tok_freq) < MAX:
                        break

            doc_tok_freq = self._get_token_count(doc_tok_freq)
            ret = BM25(self.conf, doc_tok_freq, tokens).rank()
            doc_tok_freq_new = {}

            for id, _ in ret:
                doc_tok_freq_new[id] = doc_tok_freq[id]
            doc_tok_freq_new = self._get_title(doc_tok_freq_new)

            for id in doc_tok_freq_new:
                title = doc_tok_freq_new[id]["_title"]
                output.write("{}, {}\n".format(id, title))
                logger.info("Result: {}, {}".format(id, title))

            output.write("{}\n\n".format(time.time() - start))

        output.close()

    def _get_token_count(self, doc_tok_freq):
        doc_ids = list(doc_tok_freq.keys())
        doc_ids  = sorted(doc_ids)
        for doc_id in doc_ids:
            doc_tok_freq[doc_id]["_tokens"] = int(self.token_count[doc_id - 1])

        return doc_tok_freq

    def _get_title(self, doc_tok_freq):
        doc_ids = list(doc_tok_freq.keys())
        doc_ids = sorted(doc_ids)
        for doc_id in doc_ids:
            file_id = doc_id // self.conf.max_titles
            line_no = doc_id % self.conf.max_titles
            if line_no == 0:
                file_id = file_id - 1
                line_no = self.conf.max_titles
            line = linecache.getline(self.conf.save + "/t" + str(file_id), line_no)[:-1]
            # assert doc_id == int(line[0])
            doc_tok_freq[doc_id]["_title"] = line
        return doc_tok_freq


    def _get_freq_regex(self, post):
        freqs = []
        fields = ["t", "b", "i", "c", "l", "r"]
        id = int(re.findall("^[0-9]+", post)[0])
        for f in fields:
            freq = 0
            if f in post:
                freq = int(re.findall(f + "[0-9]+", post)[0][1:])
                # if f == 't':
                #     freq *= 10
            freqs.append(freq)
        return id, freqs

    def _update_count_map(self, doc_tok_freq, token, posting, page):
        posting = posting.split("-")
        for post in posting:
            fields = ["t", "b", "i", "c", "l", "r"]
            freqs = [0] * len(fields)
            type = "I"
            start = 0
            for pos, i in enumerate(post):
                if i in fields:
                    end = pos
                    if type == "I":
                        id = int(post[start:end])
                    else:
                        index = fields.index(type)
                        freqs[index] = int(post[start:end])
                    start = end + 1
                    type = i
            index = fields.index(type)
            freqs[index] = int(post[start : len(post)])

            if page.id == -1:
                count = sum(freqs)
            else:
                count = 0
                if token in page.title:
                    count += freqs[0]

                if token in page.body:
                    count += freqs[1]

                if token in page.infobox:
                    count += freqs[2]

                if token in page.categories:
                    count += freqs[3]

                if token in page.links:
                    count += freqs[4]

                if token in page.references:
                    count += freqs[5]

            try:
                doc_tok_freq[id][token] = count
            except:
                doc_tok_freq[id] = {}
                doc_tok_freq[id][token] = count
            try:
                doc_tok_freq[id]["token_count"] += 1
            except:
                doc_tok_freq[id]["token_count"] = 1

        return doc_tok_freq
