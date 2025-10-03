# test_crawler_lab1.py
import unittest
from crawler import crawler


class TestCrawlerLab1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use your existing urls.txt; keep depth small for speed/determinism
        cls.bot = crawler(None, "urls.txt")
        cls.bot.crawl(depth=0)

    def test_get_inverted_index_shape(self):
        """get_inverted_index returns dict[int -> set[int]] and is non-empty."""
        idx = self.bot.get_inverted_index()
        self.assertIsInstance(idx, dict)
        self.assertGreater(len(idx), 0)

        for wid, postings in idx.items():
            self.assertIsInstance(wid, int, "word_id keys must be ints")
            self.assertIsInstance(postings, set, "postings must be sets of doc_ids")
            for did in postings:
                self.assertIsInstance(did, int, "doc_ids must be ints")

    def test_inverted_index_refs_only_visited_docs(self):
        """Every doc_id in postings must be a visited doc (exists in _doc_index)."""
        idx = self.bot.get_inverted_index()
        visited_doc_ids = set(self.bot._doc_index.keys())
        posting_doc_ids = set().union(*(postings for postings in idx.values())) if idx else set()
        self.assertTrue(
            posting_doc_ids.issubset(visited_doc_ids),
            "All doc_ids in the inverted index must correspond to visited documents",
        )

    def test_get_resolved_inverted_index_shape(self):
        """get_resolved_inverted_index returns dict[str -> set[str]] and is non-empty."""
        resolved = self.bot.get_resolved_inverted_index()
        self.assertIsInstance(resolved, dict)
        self.assertGreater(len(resolved), 0)

        for word, urls in resolved.items():
            self.assertIsInstance(word, str)
            self.assertTrue(word.strip(), "word keys should be non-empty strings")
            self.assertIsInstance(urls, set)
            self.assertGreater(len(urls), 0, "each word should map to >=1 URL")
            for u in urls:
                self.assertIsInstance(u, str)
                self.assertTrue(u.startswith(("http://", "https://")), "URLs should start with http(s)://")

    def test_resolved_matches_raw_index_for_sample(self):
        """Resolved URLs must match the raw postings translated via caches (spot check)."""
        raw = self.bot.get_inverted_index()
        resolved = self.bot.get_resolved_inverted_index()

        # helper maps from the crawler internals
        word_to_id = self.bot._word_id_cache                    # word -> wid
        docid_to_url = {did: meta["url"] for did, meta in self.bot._doc_index.items()}  # id -> url

        checks = 0
        for word, urlset in resolved.items():
            wid = word_to_id.get(word)
            if wid is None:
                continue  # defensive; shouldn't happen
            raw_doc_ids = raw.get(wid, set())
            translated = {docid_to_url[d] for d in raw_doc_ids if d in docid_to_url}
            self.assertEqual(urlset, translated, f"Mismatch for word '{word}'")
            checks += 1
            if checks >= 20:  # keep test fast
                break

        self.assertGreater(checks, 0, "expected to validate at least one resolved word")


if __name__ == "__main__":
    # Run with: python -m unittest -v test_crawler_lab1.py
    unittest.main(verbosity=2) # verbosity=2 for descriptive output
