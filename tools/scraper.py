from playwright.async_api import async_playwright
import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger("fanap-mcp")

async def handle_scrape_page(args: dict) -> str:
    """Scrape text content from a URL"""
    url      = args["url"]
    selector = args.get("selector", "body")

    logger.info(json.dumps({
        "tool":   "scrape_page",
        "url":    url,
        "status": "started"
    }))

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page    = await browser.new_page()

            await page.goto(url, wait_until="networkidle")
            elements = await page.query_selector_all(selector)

            results = []
            for el in elements[:20]:
                text = await el.inner_text()
                if text.strip():
                    results.append(text.strip())

            await browser.close()
            result = json.dumps(results)

        logger.info(json.dumps({
            "tool":   "scrape_page",
            "url":    url,
            "status": "success"
        }))
        return result

    except Exception as e:
        logger.error(json.dumps({
            "tool":   "scrape_page",
            "url":    url,
            "status": "error",
            "error":  str(e)
        }))
        raise

async def handle_scrape_fpl_player(args: dict) -> str:
    """Scrape FPL stats for a specific player"""
    player_name = args["player_name"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page    = await browser.new_page()

        await page.goto(
            f"https://fantasy.premierleague.com/statistics",
            wait_until="networkidle"
        )
        # search and extract player stats
        # your existing scraping logic goes here
        await browser.close()

        return json.dumps({"player": player_name, "status": "scraped"})