"""
TopAnnonces Debug - Analyze page structure
"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("Loading TopAnnonces.fr...")
    page.goto("https://www.topannonces.fr/voitures", wait_until='domcontentloaded')
    time.sleep(3)
    
    # Accept cookies
    try:
        page.locator('button:has-text("Accepter")').first.click(timeout=2000)
        print("✓ Cookies accepted")
        time.sleep(2)
    except:
        pass
    
    # Save HTML and screenshot
    page.screenshot(path="topannonces_debug.png", full_page=True)
    print("✓ Screenshot saved: topannonces_debug.png")
    
    html = page.content()
    with open("topannonces_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ HTML saved: topannonces_debug.html")
    
    # Test selectors
    print("\n🔍 Testing selectors:")
    selectors = [
        'div[class*="card"]',
        'article',
        'div[class*="annonce"]',
        'a[href*="/voiture"]',
        'div.item',
        'div.listing',
        '[data-id]',
    ]
    
    for sel in selectors:
        count = page.locator(sel).count()
        print(f"  {sel}: {count} elements")
        
        if count > 0 and count < 20:
            # Get first element text
            try:
                first = page.locator(sel).first
                text = first.inner_text()
                print(f"    First element text (100 chars): {text[:100].strip()}")
                
                # Get HTML structure
                html_sample = first.evaluate('el => el.outerHTML')
                print(f"    HTML sample: {html_sample[:200]}...")
            except Exception as e:
                print(f"    Error getting sample: {e}")
    
    # Check for specific text content
    print("\n💰 Looking for prices:")
    price_elements = page.locator(':has-text("€")').all()
    print(f"  Found {len(price_elements)} elements with €")
    for i, elem in enumerate(price_elements[:5]):
        try:
            text = elem.inner_text()
            if '€' in text:
                print(f"    {i+1}. {text[:50]}")
        except:
            pass
    
    browser.close()
    print("\n✅ Debug complete! Upload topannonces_debug.html")
