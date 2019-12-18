# Wikipedia-Search-Engine
A wikipedia based search engine. The inverted index of Wikipedia data is made using Block Sort Based Indexing. The search takes approximately 0.5 seconds and enters the retreives the top 10 results via Tf-Idf ranking.

Steps to create index:
python3 index.py <path to data dump> <path to index file>

Steps to perform search:
python3 wiki_search.py 
