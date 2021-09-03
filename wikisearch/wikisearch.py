import argparse
from .index import Index
from .utils.logger import logger


def create_index(conf):
    logger.info("Starting index creation")
    index = Index(conf)
    index.build()


def search_index(conf):
    index = Index(conf)
    ret = index.search()
    print(ret)


def main():
    parser = argparse.ArgumentParser(description="Index and search wiki xmls")
    parser.add_argument("--run", type=str, required=True)
    parser.add_argument(
        "--file", type=str, default="./data/enwiki-latest-pages-articles17.xml"
    )
    parser.add_argument("--stats", type=str, default="./invertedindex_stat.txt")
    parser.add_argument("--save", type=str, default="./inverted_index/")
    parser.add_argument("--query", type=str)
    conf = parser.parse_args()

    if conf.run == "index":
        create_index(conf)
    elif conf.run == "search":
        search_index(conf)


if __name__ == "__main__":
    main()
