from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from playwright.sync_api import sync_playwright

from typing import Optional
app = FastAPI(title="Web Scraper API")

# Store Playwright objects
playwright = None

browser = None

browser_context = None

# Add these lines after creating the FastAPI app

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/product-price")
def get_product_price(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        print(f"Navigating to the product page {url}")
        price_details = dict()
        # Scraping the price details
        print(f"Scraping the price details for the product {url}")
        price_element = page.query_selector(".a-price .a-offscreen")
        price_discount_percentage = page.query_selector(".reinventPriceSavingsPercentageMargin")
        mrp_price_element = page.query_selector(".a-size-small.aok-offscreen")
        if mrp_price_element:
            mrp_price = mrp_price_element.inner_text()
            mrp_price = mrp_price.replace("M.R.P.:", "")
            price_details['mrp_price'] = mrp_price
        if price_element:
            price = price_element.inner_text()
            price_details['price'] = price
        if price_discount_percentage:
            discount_percentage = price_discount_percentage.inner_text()
            price_details['discount_percentage'] = discount_percentage

        browser.close()
        return {"price": price_details}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False) 