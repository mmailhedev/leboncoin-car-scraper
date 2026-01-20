"""
Quick CAPTCHA Detector - Test Multiple Car Sites
=================================================
Tests if sites are accessible without CAPTCHA protection
"""

from playwright.sync_api import sync_playwright
import time

SITES_TO_TEST = [
    # Petites annonces françaises
    {
        'name': 'ParuVendu.fr',
        'url': 'https://www.paruvendu.fr/voiture-occasion/',
        'category': 'Petites annonces FR'
    },
    {
        'name': 'OuestFrance-Auto.com',
        'url': 'https://www.ouestfrance-auto.com/occasion/',
        'category': 'Petites annonces FR'
    },
    {
        'name': 'TopAnnonces.fr',
        'url': 'https://www.topannonces.fr/voitures',
        'category': 'Petites annonces FR'
    },
    
    # Sites spécialisés
    {
        'name': 'AramisAuto.com',
        'url': 'https://www.aramisauto.com/voitures-occasion',
        'category': 'Mandataire FR'
    },
    {
        'name': 'Lacentrale.fr',
        'url': 'https://www.lacentrale.fr/listing?makesModelsCommercialNames=',
        'category': 'Petites annonces FR'
    },
    
    # Sites européens
    {
        'name': 'Mobile.de',
        'url': 'https://www.mobile.de/auto/',
        'category': 'Allemagne'
    },
    {
        'name': 'AutoTrader.co.uk',
        'url': 'https://www.autotrader.co.uk/car-search',
        'category': 'UK'
    },
    
    # Enchères publiques
    {
        'name': 'Agorastore.fr',
        'url': 'https://www.agorastore.fr/vehicules',
        'category': 'Enchères publiques'
    },
    {
        'name': 'Interencheres.com',
        'url': 'https://www.interencheres.com/fr/recherche/vehicules',
        'category': 'Enchères'
    },
]


def test_site(page, site_info):
    """Test if a site is accessible"""
    print(f"\n{'='*70}")
    print(f"Testing: {site_info['name']} ({site_info['category']})")
    print(f"URL: {site_info['url']}")
    print('-'*70)
    
    try:
        # Navigate to site
        page.goto(site_info['url'], wait_until='domcontentloaded', timeout=15000)
        time.sleep(3)
        
        # Get page content
        content = page.content().lower()
        title = page.title()
        
        print(f"✓ Loaded: {title[:60]}...")
        
        # Check for CAPTCHA indicators
        captcha_keywords = [
            'captcha', 'datadome', 'cloudflare', 'recaptcha',
            'bot protection', 'access denied', 'blocked',
            'challenge', 'verification'
        ]
        
        captcha_detected = any(keyword in content for keyword in captcha_keywords)
        
        if captcha_detected:
            print("❌ STATUS: CAPTCHA/Protection detected")
            result = 'BLOCKED'
        else:
            # Try to find some common elements
            has_articles = page.locator('article').count() > 0
            has_links = page.locator('a[href*="voiture"], a[href*="car"], a[href*="vehicule"]').count() > 0
            
            if has_articles or has_links:
                print("✅ STATUS: ACCESSIBLE - Listings found!")
                result = 'ACCESSIBLE'
            else:
                print("⚠️  STATUS: Loaded but no listings detected")
                result = 'UNCERTAIN'
        
        # Quick selector test
        print("\nQuick element check:")
        selectors = ['article', 'div[class*="card"]', 'a[href*="voiture"]', 'a[href*="vehicule"]']
        for sel in selectors:
            count = page.locator(sel).count()
            if count > 0:
                print(f"  ✓ {sel}: {count} elements")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:100]}")
        return 'ERROR'


def main():
    print("\n" + "="*70)
    print("🔍 CAR WEBSITES CAPTCHA DETECTOR")
    print("="*70)
    print("Testing multiple car listing sites for accessibility...")
    print("="*70)
    
    results = {
        'ACCESSIBLE': [],
        'BLOCKED': [],
        'UNCERTAIN': [],
        'ERROR': []
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='fr-FR',
        )
        page = context.new_page()
        
        for i, site in enumerate(SITES_TO_TEST, 1):
            print(f"\n[{i}/{len(SITES_TO_TEST)}]", end=" ")
            result = test_site(page, site)
            results[result].append(site)
            time.sleep(2)  # Be polite
        
        browser.close()
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if results['ACCESSIBLE']:
        print(f"\n✅ ACCESSIBLE SITES ({len(results['ACCESSIBLE'])}):")
        for site in results['ACCESSIBLE']:
            print(f"  • {site['name']} - {site['url']}")
    
    if results['UNCERTAIN']:
        print(f"\n⚠️  UNCERTAIN ({len(results['UNCERTAIN'])}):")
        for site in results['UNCERTAIN']:
            print(f"  • {site['name']} - {site['url']}")
    
    if results['BLOCKED']:
        print(f"\n❌ BLOCKED ({len(results['BLOCKED'])}):")
        for site in results['BLOCKED']:
            print(f"  • {site['name']}")
    
    if results['ERROR']:
        print(f"\n💥 ERRORS ({len(results['ERROR'])}):")
        for site in results['ERROR']:
            print(f"  • {site['name']}")
    
    print("\n" + "="*70)
    
    if results['ACCESSIBLE']:
        print(f"\n🎯 RECOMMENDATION: Use {results['ACCESSIBLE'][0]['name']}")
        print(f"   URL: {results['ACCESSIBLE'][0]['url']}")
        print("\n✅ This site is accessible and ready for scraping!")
    else:
        print("\n⚠️  No fully accessible sites found.")
        print("Consider using demo data or undetected-chromedriver.")
    
    print()


if __name__ == "__main__":
    main()
