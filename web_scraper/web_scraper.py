import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List
import concurrent.futures

class ArticleScraper:
    def __init__(self, output_dir: str):  # Fixed constructor method name
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(f"Output directory set to: {output_dir}")

    def fetch_sitemaps(self, main_sitemap_url: str) -> List[str]:
        print(f"Fetching sitemaps from: {main_sitemap_url}")
        response = requests.get(main_sitemap_url)
        if response.status_code != 200:
            print(f"Failed to fetch sitemap index. Status code: {response.status_code}")
            return []
        soup = BeautifulSoup(response.content, 'lxml')
        sitemap_urls = [tag.text for tag in soup.find_all('loc')]
        print(f"Found {len(sitemap_urls)} sitemap URLs.")
        return sitemap_urls

    def fetch_article_urls(self, sitemap_url: str) -> List[str]:
        print(f"Fetching articles from sitemap: {sitemap_url}")
        response = requests.get(sitemap_url)
        if response.status_code != 200:
            print(f"Failed to fetch sitemap. Status code: {response.status_code}")
            return []
        soup = BeautifulSoup(response.content, 'lxml')
        article_urls = [tag.text for tag in soup.find_all('loc')]
        print(f"Found {len(article_urls)} article URLs.")
        return article_urls

    def scrape_article(self, article_url: str) -> dict:
        print(f"Scraping article: {article_url}")
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to fetch article. Status code: {response.status_code}")
            return None
        soup = BeautifulSoup(response.content, 'lxml')
        metadata = {}
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if script_tag:
            try:
                metadata = json.loads(script_tag.string)
            except json.JSONDecodeError:
                print(f"Error parsing JSON metadata for {article_url}")
                return None
        return {
            "url": metadata.get('url', article_url),
            "post_id": metadata.get('identifier', 'unknown'),
            "title": metadata.get('headline', 'unknown'),
            "keywords": metadata.get('keywords', [] if not isinstance(metadata.get('keywords'), str) else metadata.get('keywords').split(',')),
            "thumbnail": metadata.get('image', {}).get('url', 'unknown') if isinstance(metadata.get('image'), dict) else 'unknown',
            "publication_date": metadata.get('datePublished', 'unknown'),
            "last_updated_date": metadata.get('dateModified', 'unknown'),
            "author": metadata.get('author', {}).get('name', 'unknown') if isinstance(metadata.get('author'), dict) else 'unknown',
            "description": metadata.get('description', 'unknown'),
            "lang": metadata.get('inLanguage', 'unknown'),
            "classes": metadata.get('@type', [] if not isinstance(metadata.get('@type'), str) else [metadata.get('@type')]),
            "word_count": len("\n".join([p.get_text() for p in soup.find_all('p')]).split()),
            "full_text": "\n".join([p.get_text() for p in soup.find_all('p')])
        }

    def save_articles(self, articles: List[dict], year: int, month: int):
        file_name = f"articles_{year}_{month:02}.json"
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(articles, json_file, ensure_ascii=False, indent=4)
        print(f"Saved {len(articles)} articles to {file_path}")

    def process_sitemaps(self, main_sitemap_url: str, article_limit: int):
        sitemaps = self.fetch_sitemaps(main_sitemap_url)
        total_articles_scraped = 0
        if not sitemaps:
            print("No sitemaps found, exiting.")
            return
        for sitemap_url in sitemaps:
            if total_articles_scraped >= article_limit:
                break
            year_month = sitemap_url.split('/')[-1].replace('sitemap-', '').replace('.xml', '').split('-')
            try:
                year, month = int(year_month[0]), int(year_month[1])
            except (IndexError, ValueError) as e:
                print(f"Error parsing year and month from URL {sitemap_url}: {e}")
                continue
            print(f"Processing articles from {year}-{month:02d}")
            article_urls = self.fetch_article_urls(sitemap_url)
            if not article_urls:
                continue
            articles = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_article = {executor.submit(self.scrape_article, url): url for url in article_urls}
                for future in concurrent.futures.as_completed(future_to_article):
                    try:
                        article = future.result()
                        if article:
                            articles.append(article)
                            total_articles_scraped += 1
                            if total_articles_scraped >= article_limit:
                                break
                    except Exception as e:
                        print(f"Error scraping article: {e}")
            if articles:
                self.save_articles(articles, year, month)
                print(f"Total number of articles scraped so far: {total_articles_scraped}")

if __name__ == "__main__":
    main_sitemap_url = "https://www.almayadeen.net/sitemaps/all.xml"
    scraper = ArticleScraper(output_dir="scraped_articles")
    scraper.process_sitemaps(main_sitemap_url=main_sitemap_url, article_limit=10000)
