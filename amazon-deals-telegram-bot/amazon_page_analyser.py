import requests
import random
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def retrieve_deals():
    """Fetches trending deal product IDs from Amazon India Today's Deals."""
    url = "https://amazon.in"
    headers = {"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "en-US,en;q=0.5"}
    
    product_ids = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Pulls structural product IDs directly from Amazon's product grids
            for link in soup.find_all("a", href=True):
                if "/dp/" in link["href"]:
                    try:
                        asin = link["href"].split("/dp/")[1].split("/")[0].split("?")[0]
                        if len(asin) == 10 and asin not in product_ids:
                            product_ids.append(asin)
                    except Exception:
                        continue
    except Exception as e:
        print(f"Error fetching deals feed: {e}")
        
    # Fallback to standard trending tech/lifestyle product ASINs if scraping fails
    if not product_ids:
        product_ids = ["B0CHX1W1XY", "B0BMGB2TPR", "B0C93699BC", "B09V7N85S6", "B089MS8692"]
        
    return product_ids

def get_product_info(asin):
    """Scrapes clean product details using layout-agnostic fallback selectors."""
    url = f"https://amazon.in{asin}"
    headers = {"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "en-US,en;q=0.5"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return None
            
        soup = BeautifulSoup(res.content, "html.parser")
        
        # 1. Extract Title cleanly
        title_element = soup.find(id="productTitle")
        title = title_element.get_text().strip() if title_element else "Special Amazon Deal"
        if len(title) > 60:
            title = title[:57] + "..."

        # 2. Extract Price safely
        price = "Check Price on Amazon"
        price_selectors = [
            "span.a-price-whole", 
            "span.apexPriceToPay span.a-offscreen", 
            "span.a-color-price"
        ]
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price = "₹" + price_element.get_text().replace("₹", "").strip()
                break

        # 3. Extract Image safely
        img_element = soup.find(id="landingImage") or soup.find(id="imgBlkFront")
        img_url = img_element.get("src") if img_element else "https://amazon.in"

        return {
            "title": title,
            "price": price,
            "image_url": img_url,
            "link": url
        }
    except Exception as e:
        print(f"Skipping product {asin} due to format changes: {e}")
        return None
