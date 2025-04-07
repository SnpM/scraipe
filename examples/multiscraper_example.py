from scraipe.defaults import IngressRule, MultiScraper, TextScraper
from scraipe.extended import NewsScraper

# Define ingress rule for news links and TextScraper fallback
ingress_rules = [
    # Use NewsScraper for links containing "news", "article", or "story"
    IngressRule(
        r"(news|article|story)",
        scraper=NewsScraper()
    ),
    # Fallback to TextScraper
    IngressRule(
        r".*",
        scraper=TextScraper()
    ),
]

# Instantiate a new MultiScraper with our custom ingress rules
multi_scraper = MultiScraper(ingress_rules=ingress_rules, debug=True)

# Scrape a news link
link = "https://apnews.com/article/studio-ghibli-chatgpt-images-hayao-miyazaki-openai-0f4cb487ec3042dd5b43ad47879b91f4"
result = multi_scraper.scrape(link)

print ("=== News Link ===")
print("Content:", result.content[0:400])
print("Debug Info:", result.error) # Ingress debug chain stored in error

# Scrape a non-news link
link = "https://www.example.com/"
result = multi_scraper.scrape(link)

print ("\n=== Non-News Link ===")
print("Content:",result.content[0:400])
print("Debug Info:", result.error) # Ingress debug chain stored in error