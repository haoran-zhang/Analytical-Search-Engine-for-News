# Analytical-Search-Engine-for-News

Hello and welcome!

This is an analytical search engine for news, especially in financial news.

Most functions are integrated in two models, auto_update and website. 

The former one acts as automatically crawl down news article from specific news website, natrual language processing them especially the sentiment, then load the data in elasticsearch.

The latter one is a simple website wrote in Django, acts as a search entrance and results output page. Some of sensitive information has been erased.

There are much Chinese annotation and documents, because the purpose of the project is dealing with Chinese news, so that the encoding/decoding part is quit complex. I'm sorry for that.

Hope you like it!
