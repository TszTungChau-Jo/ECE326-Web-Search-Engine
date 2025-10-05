# test_crawler_lab1.py
import unittest
from crawler import crawler


class TestCrawlerLab1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the existing urls.txt
        cls.bot = crawler(None, "urls.txt")
        cls.bot.crawl(depth=0)

    def test_get_inverted_index_returns_dict(self):
        """get_inverted_index should return a dictionary."""
        # Call the required function
        idx = self.bot.get_inverted_index()
        
        # Check that it returns a dictionary type
        self.assertIsInstance(idx, dict)
        
        # Verify the dictionary is not empty (should have indexed some words)
        self.assertGreater(len(idx), 0, "Inverted index should not be empty")

    def test_inverted_index_structure(self):
        """Inverted index should map word_ids (int) to sets of doc_ids (int)."""
        # Get the inverted index
        idx = self.bot.get_inverted_index()
        
        # Check each entry in the dictionary
        for wid, postings in idx.items():
            # Keys should be word IDs (integers)
            self.assertIsInstance(wid, int, "Word IDs must be integers")
            
            # Values should be sets (for efficient lookup)
            self.assertIsInstance(postings, set, "Postings must be sets")
            
            # Each element in the set should be a document ID (integer)
            for doc_id in postings:
                self.assertIsInstance(doc_id, int, "Doc IDs must be integers")

    def test_get_resolved_inverted_index_returns_dict(self):
        """get_resolved_inverted_index should return a dictionary."""
        # Call the second required function
        resolved = self.bot.get_resolved_inverted_index()
        
        # Verify it returns a dictionary
        self.assertIsInstance(resolved, dict)
        
        # Check that the dictionary has content
        self.assertGreater(len(resolved), 0, "Resolved index should not be empty")

    def test_resolved_index_structure(self):
        """Resolved index should map words (str) to sets of URLs (str)."""
        # Get the resolved inverted index
        resolved = self.bot.get_resolved_inverted_index()
        
        # Check each entry: word -> set of URLs
        for word, urls in resolved.items():
            # Keys should be actual words (strings)
            self.assertIsInstance(word, str, "Keys must be strings (words)")
            
            # Values should be sets of URLs
            self.assertIsInstance(urls, set, "Values must be sets of URLs")
            
            # Each URL in the set should be a string starting with http:// or https://
            for url in urls:
                self.assertIsInstance(url, str, "URLs must be strings")
                self.assertTrue(
                    url.startswith("http://") or url.startswith("https://"),
                    "URLs should start with http:// or https://"
                )

    def test_doc_index_has_required_fields(self):
        """Document index entries must have url, title, and desc fields."""
        # Verify we indexed at least one document
        self.assertGreater(len(self.bot._doc_index), 0, "Should have indexed documents")
        
        # Check each document's metadata structure
        for doc_id, meta in self.bot._doc_index.items():
            # Lab requirement: each document must have these three fields
            self.assertIn("url", meta, "Missing 'url' field")
            self.assertIn("title", meta, "Missing 'title' field")
            self.assertIn("desc", meta, "Missing 'desc' field")

    def test_descriptions_exist(self):
        """At least some documents should have descriptions."""
        # Count how many documents have non-empty descriptions
        docs_with_desc = sum(1 for meta in self.bot._doc_index.values() if meta["desc"])
        
        # Lab requires storing "first 3 lines" as description - verify it's working
        self.assertGreater(docs_with_desc, 0, "Some documents should have descriptions")

    def test_ignored_words_filtered(self):
        """Common words like 'the', 'of', 'and' should be filtered out."""
        # Define the set of ignored words from the crawler
        ignored = {'the', 'of', 'at', 'on', 'in', 'is', 'it', 'a', 'and', 'or'}
        
        # Check if any ignored words made it into the word cache (lexicon)
        found_ignored = ignored.intersection(self.bot._word_id_cache.keys())
        
        # There should be no overlap - ignored words shouldn't be indexed
        self.assertEqual(len(found_ignored), 0, f"Found ignored words: {found_ignored}")

if __name__ == "__main__":
    # Run with: python -m unittest -v test_crawler_lab1.py
    unittest.main(verbosity=2) # verbosity=2 for descriptive output
