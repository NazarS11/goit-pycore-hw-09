import scrapy
import json
from scrapy.crawler import CrawlerProcess
from os import path

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]
    
    quotes = []

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            author_page = quote.xpath("span/small/following-sibling::a/@href").get()
            author_url = response.urljoin(author_page)
            
            quote_text = quote.xpath("span[@class='text']/text()").get()
            author = quote.xpath("span/small[@class='author']/text()").get()
            tags = quote.xpath("div[@class='tags']/a[@class='tag']/text()").extract()
            
            self.quotes.append({
                'author': author,
                'quote': quote_text,
                'tags': tags
            })
            
            yield response.follow(author_url, self.parse_author, meta={'author': author})

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
        else:
            with open('quotes.json', 'w', encoding='utf-8') as f:
                json.dump(self.quotes, f, ensure_ascii=False, indent=4)
    
    def parse_author(self, response):
        author = response.meta['author']
              
        born_date = response.xpath("//span[@class='author-born-date']/text()").get()
        born_date = born_date.strip() if born_date else ''
        
        born_location = response.xpath("//span[@class='author-born-location']/text()").get()
        born_location = born_location.strip().replace('in ', '') if born_location else ''
        
        description = response.xpath("//div[@class='author-description']/text()").getall()
        description = ' '.join(description).strip() if description else ''

        author_data = {
            'fullname': author,
            'born_date': born_date,
            'born_location': born_location,
            'description': description
        }

        if path.exists('authors.json'):
            with open('authors.json', 'r', encoding='utf-8') as f:
                try:
                    authors = json.load(f)
                except json.JSONDecodeError:
                    authors = []
        else:
            authors = []
        
        authors.append(author_data)
        
        with open('authors.json', 'w', encoding='utf-8') as f:
            json.dump(authors, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
