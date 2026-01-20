"""
LeBonCoin Scraper with Anti-Detection
======================================
Uses stealth techniques to bypass DataDome CAPTCHA
"""

from playwright.sync_api import sync_playwright
import time
import random

def create_stealth_context(browser):
    """Create a browser context with stealth settings"""
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        
        # Real user agent
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Accept language
        locale='fr-FR',
        timezone_id='Europe/Paris',
        
        # Geolocation (France)
        geolocation={'longitude': 2.3522, 'latitude': 48.8566},
        permissions=['geolocation'],
        
        # Extra HTTP headers
        extra_http_headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    )
    
    return context


def test_leboncoin_access():
    """Test if we can access LeBonCoin with stealth mode"""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        # Create stealth context
        context = create_stealth_context(browser)
        page = context.new_page()
        
        # Override navigator.webdriver
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['fr-FR', 'fr', 'en-US', 'en']
            });
            
            // Chrome detection
            window.chrome = {
                runtime: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("🚀 Testing LeBonCoin access with stealth mode...")
        
        # Add random delay
        time.sleep(random.uniform(2, 4))
        
        # Navigate
        url = "https://www.leboncoin.fr/recherche?category=2&locations=France&price=0-30000"
        print(f"Loading: {url}")
        
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # Wait and add human-like behavior
        time.sleep(random.uniform(3, 5))
        
        # Random mouse movement
        page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        
        # Check for CAPTCHA
        page_content = page.content()
        
        if 'captcha-delivery.com' in page_content:
            print("❌ CAPTCHA detected - DataDome is still blocking")
            print("\n💡 Alternative solutions needed:")
            print("   1. Use residential proxy")
            print("   2. Rotate IP addresses")
            print("   3. Use LeBonCoin API if available")
            print("   4. Manual browser automation with undetected-chromedriver")
            
            # Save HTML
            with open("captcha_page.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            print("   Saved captcha_page.html for analysis")
            
        else:
            print("✅ No CAPTCHA detected!")
            
            # Try to find listings
            time.sleep(2)
            
            # Test multiple selectors
            selectors_to_test = [
                '[data-qa-id="aditem_container"]',
                'article',
                'a[href*="/ad/"]',
                'div[class*="card"]',
                'div[class*="ad"]',
                '[data-testid]',
                'div[role="article"]',
            ]
            
            print("\n🔍 Testing selectors:")
            for selector in selectors_to_test:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"✓ {selector}: {count} elements")
                        
                        # Get sample HTML
                        if count > 0:
                            first = page.locator(selector).first
                            html = first.evaluate('el => el.outerHTML')
                            print(f"  Sample: {html[:300]}...")
                    else:
                        print(f"✗ {selector}: 0 elements")
                except Exception as e:
                    print(f"✗ {selector}: Error - {e}")
            
            # Save successful HTML
            with open("success_page.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            print("\n✓ Saved success_page.html")
            
            # Screenshot
            page.screenshot(path="success_page.png", full_page=True)
            print("✓ Saved success_page.png")
        
        browser.close()


if __name__ == "__main__":
    test_leboncoin_access()
