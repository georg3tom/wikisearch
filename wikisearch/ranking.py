from math import log10
from operator import itemgetter


class BM25:
    def __init__(self, conf, data, tokens, k=1.2, b=0.5):
        self.conf = conf
        self.k = k
        self.b = b
        self.data = data
        self.tokens = tokens

        with open(self.conf.doc_num, "r") as f:
            self.no_of_docs, total_tokens = f.read().splitlines()
            self.no_of_docs = int(self.no_of_docs)
            self.avg_len = int(total_tokens) / self.no_of_docs

    def _sort(self, scores):
        sorted_rank = sorted(scores.items(), key=itemgetter(1), reverse=True)
        if len(sorted_rank) > self.conf.max_output:
            sorted_rank = sorted_rank[: self.conf.max_output]
        return sorted_rank

    def rank(self):
        scores = {}
        for id in self.data:
            scores[id] = 0
            for token in self.tokens:
                count = 0
                if token in self.data[id]:
                    count = self.data[id][token]
                if count == 0:
                    idf = 0
                else:
                    idf = log10(self.no_of_docs / count)

                idf = idf * (self.k + 1) * count
                d = (
                    self.k
                    * (
                        (1 - self.b)
                        + self.b * (int(self.data[id]["_tokens"]) / self.avg_len)
                    )
                    + count
                )
                scores[id] += idf / d

        return self._sort(scores)
