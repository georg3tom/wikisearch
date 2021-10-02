from .parser import WikiParser
from .page import Page
from .utils.logger import logger
from .search import Search
from pathlib import Path
from collections import Counter
import json


class Index:
    def __init__(self, conf):
        self.conf = conf
        self._block_pre = self.conf.save + "/b"
        self._block_no = 0
        self._block = Path(self._block_pre + str(self._block_no))
        self.doc_count = 0

        Path(self.conf.save).mkdir(parents=True, exist_ok=True)

        self.max_size = 1000000
        self.dict = {}

        self._index_no = 0
        self._index_pre = self.conf.save + "/i"
        self._index = Path(self._index_pre + str(self._index_no))
        self.current_token_count = 0

        self._title_no = 0
        self._title_pre = self.conf.save + "/t"
        self._title = Path(self._title_pre + str(self._title_no))
        self.title_count = 0

        self.max_tokens = self.conf.max_tokens
        self.meta = {}
        self.meta_path = self.conf.meta_path
        self.first_token = ""
        self.last_token = ""
        self.doc_num = self.conf.doc_num

        self.token_count = 0

    def build(self):
        parser = WikiParser()
        self._output_index = open(self._index, "w")
        self._output_title = open(self._title, "w")
        self._token_count_file = open(Path(self.conf.token_count), "w")
        parser.parse(self.conf, self.index)
        self._save_block()
        self._merge()
        self._clean_stuff()

    def _clean_stuff(self):
        self._save_index(end=True)
        self._save_title(end=True)
        self._token_count_file.close()

        with open(self.meta_path, "w") as f:
            f.write(json.dumps(self.meta))

        with open(self.doc_num, "w") as f:
            f.write(str(self.doc_count))
            f.write("\n" + str(self.token_count))

        block_files = Path(self.conf.save).glob("b*")
        for block_file in block_files:
            block_file.unlink()

        size_of_save = sum(
            file.stat().st_size for file in Path(self.conf.save).rglob("*")
        )
        size_of_save = size_of_save / 1024 ** 3
        with open(self.conf.stats, "w") as f:
            f.write(str(size_of_save) + "\n")
            f.write(str(self._index_no) + "\n")
            f.write(str(self.token_count))

    def index(self, page: Page):
        self.doc_count = page.id
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

        for token in unq:
            counts = [
                title_c[token] * 5,
                body_c[token],
                categories_c[token],
                references_c[token],
                infobox_c[token],
                links_c[token],
            ]
            self._add_to_dict(page.id, token, counts)
        self._output_title.write("{}\n".format(page.title_orginal.strip()))
        self._token_count_file.write("{}\n".format(len(unq)))
        self._save_title()

    def _merge(self):
        b_files = Path(self.conf.save).glob("b*")
        b_files = [open(block_file) for block_file in b_files]
        self.last_token = ""
        lines = [block_file.readline()[:-1] for block_file in b_files]

        index = 0

        for b_file in b_files:
            if lines[index] == "":
                b_files.pop(index)
                lines.pop(index)
            else:
                index += 1

        while len(b_files) > 0:

            s_token = lines.index(min(lines))
            line = lines[s_token]
            current_term, current_postings = line.split()

            if current_term == self.last_token:
                self._output_index.write("-%s" % current_postings)
            else:
                self._save_index()
                if self.current_token_count != 0:
                    self._output_index.write("\n")
                if self.current_token_count == 1:
                    self.first_token = current_term
                self._output_index.write("%s %s" % (current_term, current_postings))
                self.last_token = current_term

            lines[s_token] = b_files[s_token].readline()[:-1]

            if lines[s_token] == "":
                b_files[s_token].close()
                b_files.pop(s_token)
                lines.pop(s_token)

    def _add_to_dict(self, id, token, counts):
        if self.max_size < len(self.dict):
            self._save_block()

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

    def _save_index(self, end=False):
        self.current_token_count += 1
        self.token_count += 1
        if self.current_token_count > self.conf.max_tokens or end:
            logger.info("Writing index {}".format(self._index))
            self.current_token_count = 0
            self._index_no += 1
            self.meta[self._index.name] = {
                "first": str(self.first_token),
                "last": str(self.last_token),
            }
            self._output_index.close()
            self._index = Path(self._index_pre + str(self._index_no))
            if end == False:
                self._output_index = open(self._index, "w")

    def _save_title(self, end=False):
        self.title_count += 1
        if self.title_count == self.conf.max_titles or end:
            logger.info("Writing title {}".format(self._title))
            self.title_count = 0
            self._title_no += 1
            self._output_title.close()
            self._title = Path(self._title_pre + str(self._title_no))
            if end == False:
                self._output_title = open(self._title, "w")

    def _save_block(self):
        logger.info("Writing block {}".format(self._block))
        sort_dict = sorted(self.dict)
        with open(self._block, "w") as f:
            for token in sort_dict:
                f.write("{} {}\n".format(token, "-".join(self.dict[token])))
        self._block_no += 1
        self._block = Path(self._block_pre + str(self._block_no))
        self.dict = {}

    def search(self):
        Search(self.conf)
