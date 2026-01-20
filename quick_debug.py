"""
Quick debug script - Run this in your GitHub Codespace
Saves HTML and screenshot to analyze selectors
"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Go to LeBonCoin
    url = "https://www.leboncoin.fr/recherche?category=2&locations=France&price=0-30000"
    print(f"Loading: {url}")
    page.goto(url, wait_until='networkidle')
    
    time.sleep(3)
    
    # Accept cookies
    try:
        page.locator('[data-qa-id="didomi-notice-agree-button"]').click(timeout=2000)
        print("✓ Cookies accepted")
        time.sleep(2)
    except:
        print("No cookie banner")
    
    # Save screenshot
    page.screenshot(path="leboncoin_debug.png", full_page=True)
    print("✓ Screenshot saved: leboncoin_debug.png")
    
    # Save HTML
    html = page.content()
    with open("leboncoin_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ HTML saved: leboncoin_debug.html")
    
    # Test selectors
    print("\n🔍 Testing selectors:")
    
    selectors = [
        '[data-qa-id="aditem_container"]',
        '[data-test-id="ad-card"]',
        'article',
        'a[href*="/ad/"]',
        'div[data-qa-id]',
    ]
    
    for sel in selectors:
        try:
            count = page.locator(sel).count()
            print(f"  {sel}: {count} elements")
            if count > 0 and count < 100:
                # Show first element's HTML
                first = page.locator(sel).first.evaluate('el => el.outerHTML')
                print(f"    Sample: {first[:200]}...")
        except Exception as e:
            print(f"  {sel}: Error")
    
    browser.close()
    print("\n✅ Done! Upload the HTML file here so I can find the right selectors")
