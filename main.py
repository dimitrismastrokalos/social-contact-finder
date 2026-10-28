import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_social_profiles(query, max_results=10):
    print(f"🔍 Searching for social profiles: '{query}'...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        await page.goto(search_url)
        await page.wait_for_timeout(2000)
        
        results = []
        search_results = await page.locator('div.g').all()
        
        for result in search_results[:max_results]:
            try:
                title_elem = result.locator('h3')
                link_elem = result.locator('a')
                snippet_elem = result.locator('div.VwiC3b')
                
                title = await title_elem.text_content() if await title_elem.count() > 0 else "N/A"
                link = await link_elem.get_attribute('href') if await link_elem.count() > 0 else "N/A"
                snippet = await snippet_elem.text_content() if await snippet_elem.count() > 0 else "N/A"
                
                if link != "N/A" and "google.com" not in link:
                    item = {
                        "Title": title.strip(),
                        "Profile URL": link,
                        "Snippet": snippet.strip()
                    }
                    results.append(item)
                    print(f"✅ Found: {title.strip()}")
            except Exception:
                continue
                
        await browser.close()
        
        if results:
            with open("social_leads.csv", mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"\n💾 Saved {len(results)} profiles to 'social_leads.csv'")

if __name__ == "__main__":
    search_query = 'site:linkedin.com/in/ "Marketing Manager" "Athens"'
    asyncio.run(scrape_social_profiles(search_query, max_results=10))