import pytest
from crawler import crawler

def test_inverted_index_with_existing_urls():
    # initialize crawler with your existing urls.txt
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=0)

    # get inverted index
    inverted = bot.get_inverted_index()

    # --- sanity checks ---
    # It should be a dictionary
    assert isinstance(inverted, dict)

    # Values should all be sets of doc_ids
    assert all(isinstance(doc_ids, set) for doc_ids in inverted.values())

    # Should not be empty since example.com has words
    assert len(inverted) > 0

    # At least one doc_id in inverted index should correspond to a doc in doc_index
    all_doc_ids = {did for doc_ids in inverted.values() for did in doc_ids}
    for did in all_doc_ids:
        assert did in bot._doc_index
