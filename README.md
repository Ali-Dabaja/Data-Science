Week 1 Report: Web Scraping with Python

Project Overview:

Objective: Created a Python script to scrape articles from the Al Mayadeen website, extract metadata and content, and save the data in JSON files organized by month.
Accomplishments:

Environment Setup:

Installed Python and configured PyCharm as the development environment.
Installed the required libraries: requests, beautifulsoup4, and lxml.
Sitemap Parsing:

Developed a class to parse the main sitemap index and retrieve monthly sitemap URLs.
Implemented methods to extract article URLs from each monthly sitemap efficiently.
Article Scraping:

Built a scraper to fetch and parse individual article pages.
Successfully extracted key metadata, including post ID, title, keywords, publication date, and author.
Extracted the full article text by capturing content from <p> tags in the HTML.
Data Storage:

Created a utility to store the extracted data into JSON files.
Organized JSON files by year and month, naming them accordingly (e.g., articles_2024_08.json).
Error Handling:

Implemented error handling to manage network issues and unexpected data formats.
Ensured that the script can continue processing even if some articles or sitemaps fail to load.
Testing:

Tested the script with a limited number of articles to verify correctness.
Verified that the data is stored accurately in the expected JSON format.
Current Progress:

The script is functional, capable of parsing sitemaps, scraping articles, and saving data in an organized manner.
Successfully processed several monthly sitemaps and stored articles in the appropriate JSON files.
Next Steps:

Scale up the script to handle up to 10,000 articles.
Optimize the script for better performance and reliability with large datasets.
