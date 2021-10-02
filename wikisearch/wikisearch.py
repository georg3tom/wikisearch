import argparse
from .index import Index
from .utils.logger import logger
from pathlib import Path


def create_index(conf):
    logger.info("Starting index creation")
    index = Index(conf)
    index.build()


def search_index(conf):
    logger.info("Starting search")
    index = Index(conf)
    index.search()


def main():
    parser = argparse.ArgumentParser(description="Index and search wiki xmls")
    parser.add_argument("--run", type=str, required=True)
    parser.add_argument(
        "--file", type=str, default="./data/enwiki-latest-pages-articles17.xml"
    )
    parser.add_argument("--stats", type=str, default="./stats.txt")
    parser.add_argument("--save", type=str, default="./inverted_index/")
    parser.add_argument("--query", type=str, default="./queries.txt")
    parser.add_argument("--result", type=str, default="./queries_op.txt")
    parser.add_argument("--max_tokens", type=int, default=10000)
    parser.add_argument("--max_titles", type=int, default=10000)
    parser.add_argument("--max_output", type=int, default=10)
    conf = parser.parse_args()
    conf.meta_path = Path(conf.save + "/meta.json")
    conf.token_count = Path(conf.save + "/token_count")
    conf.doc_num = Path(conf.save + "/doc_num.txt")

    if conf.run == "index":
        create_index(conf)
    elif conf.run == "search":
        search_index(conf)


if __name__ == "__main__":
    main()
