"""
TopAnnonces.fr Car Scraper - Production Ready
Scrapes real car listings from TopAnnonces.fr without CAPTCHA
"""

import logging
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
import csv

class TopAnnoncesScraper:
    def __init__(self, max_results=50, headless=True):
        # URL directe vers la section véhicules (plus de voitures)
        self.base_url = "https://www.topannonces.fr/vehicules"
        self.max_results = max_results
        self.headless = headless
        self.cars = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def scrape_cars(self):
        """Main scraping method"""
        self.logger.info("\n" + "="*70)
        self.logger.info("Starting REAL scraping from TopAnnonces.fr")
        self.logger.info(f"Target: {self.max_results} listings")
        self.logger.info("="*70)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            try:
                # Navigate to listings page
                self.logger.info(f"Navigating to: {self.base_url}")
                page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                
                # Accept cookies if present
                try:
                    cookie_selectors = [
                        'button:has-text("Accepter")',
                        'button:has-text("Accept")',
                        '[class*="accept"]'
                    ]
                    for selector in cookie_selectors:
                        try:
                            page.locator(selector).first.click(timeout=2000)
                            self.logger.info("✓ Accepted cookies")
                            time.sleep(2)
                            break
                        except:
                            continue
                except:
                    pass
                
                page_num = 1
                previous_count = 0
                same_count_iterations = 0
                
                while len(self.cars) < self.max_results:
                    self.logger.info(f"\n📄 Scraping page {page_num}...")
                    
                    # Wait for content to load
                    time.sleep(3)  # Augmenté de 2 à 3 secondes
                    
                    # Find listing cards - Angular Material structure
                    # Les annonces sont dans des <a> qui contiennent des <mat-card>
                    cards = page.locator('a[href*="/"] mat-card').all()
                    
                    self.logger.info(f"Found {len(cards)} potential listings on this page")
                    
                    if len(cards) == 0:
                        self.logger.warning("No cards found on page")
                        break
                    
                    # Detect if we're stuck (same number of results)
                    if len(cards) == previous_count:
                        same_count_iterations += 1
                        if same_count_iterations >= 2:
                            self.logger.info("Same content detected, stopping pagination")
                            break
                    else:
                        same_count_iterations = 0
                    previous_count = len(cards)
                    
                    extracted = 0
                    for card in cards:
                        if len(self.cars) >= self.max_results:
                            break
                        
                        car_data = self._extract_listing_data(card)
                        if car_data:
                            # Vérifier qu'on n'a pas déjà cette annonce (éviter doublons)
                            if not any(c['url'] == car_data['url'] for c in self.cars if c['url']):
                                self.cars.append(car_data)
                                extracted += 1
                    
                    self.logger.info(f"✓ Extracted {extracted} NEW valid listings from this page (total: {len(self.cars)})")
                    
                    # Try to go to next page
                    if not self._go_to_next_page(page):
                        break
                    
                    page_num += 1
                
            except Exception as e:
                self.logger.error(f"Error during scraping: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
            finally:
                browser.close()
        
        self.logger.info("\n" + "="*70)
        self.logger.info(f"✓ Scraping complete - {len(self.cars)} real listings extracted")
        self.logger.info("="*70)
        
        return self.cars
    
    def _extract_listing_data(self, card):
        """Extract data from a single Angular Material card"""
        try:
            # Extract title from mat-card-title
            title = None
            try:
                title_elem = card.locator('mat-card-title').first
                if title_elem.count() > 0:
                    title = title_elem.inner_text().strip()
            except:
                pass
            
            if not title:
                return None
            
            # Extract location from mat-card-subtitle
            location = ""
            try:
                location_elem = card.locator('mat-card-subtitle').first
                if location_elem.count() > 0:
                    location = location_elem.inner_text().strip()
            except:
                pass
            
            # Extract description from mat-card-content
            description = ""
            try:
                desc_elem = card.locator('mat-card-content p').first
                if desc_elem.count() > 0:
                    description = desc_elem.inner_text().strip()
            except:
                pass
            
            # Extract price from mat-card-actions
            price = ""
            try:
                # Le prix est dans un <span> dans mat-card-actions
                price_elem = card.locator('mat-card-actions span:not([class*="button"])').first
                if price_elem.count() > 0:
                    price_text = price_elem.inner_text().strip()
                    if '€' in price_text:
                        price = price_text
            except:
                pass
            
            # Extract URL from parent <a> tag
            url = ""
            try:
                parent_link = card.locator('..').first  # Parent <a> element
                href = parent_link.get_attribute('href')
                if href:
                    if not href.startswith('http'):
                        url = f"https://www.topannonces.fr{href}"
                    else:
                        url = href
            except:
                pass
            
            # Parse data from title and description
            brand, model = self._parse_brand_model(title)
            year = self._extract_year(f"{title} {description}")
            mileage = self._extract_mileage(description)
            fuel_type = self._extract_fuel(f"{title} {description}")
            price_num = self._extract_price(price)
            
            # Filter: only keep if URL contains car-related paths OR has car keywords
            # TopAnnonces URLs pour voitures: /voiture-occasion/ ou /vehicules/
            is_car_url = url and ('/voiture' in url.lower() or '/vehicule' in url.lower())
            
            # Backup filter si pas d'URL: chercher des mots-clés voiture
            car_keywords = ['renault', 'peugeot', 'citroen', 'volkswagen', 'bmw', 'mercedes',
                           'audi', 'ford', 'opel', 'toyota', 'nissan', 'fiat', 'seat',
                           'voiture', 'auto', 'dti', 'tdi', 'hdi', 'diesel', 'essence', 
                           'km', 'kilométrage', 'boite', 'cv', 'ch', 'break', 'berline',
                           'suv', '4x4', 'cabriolet', 'coupé']
            
            title_lower = title.lower()
            desc_lower = description.lower()
            has_car_keyword = any(keyword in title_lower or keyword in desc_lower for keyword in car_keywords)
            
            # Accepter si URL de voiture OU au moins 1 mot-clé
            if not (is_car_url or has_car_keyword):
                return None
            
            return {
                'title': title,
                'brand': brand,
                'model': model,
                'year': year,
                'mileage': mileage,
                'price': price,
                'price_numeric': price_num,
                'fuel_type': fuel_type,
                'location': location,
                'description': description[:200],
                'url': url
            }
        
        except Exception as e:
            self.logger.debug(f"Error extracting data: {e}")
            return None
    
    def _parse_brand_model(self, title):
        """Extract brand and model from title"""
        brands = ['Renault', 'Peugeot', 'Citroën', 'Volkswagen', 'BMW', 'Mercedes',
                 'Audi', 'Ford', 'Opel', 'Toyota', 'Nissan', 'Fiat', 'Seat',
                 'Skoda', 'Volvo', 'Mazda', 'Honda', 'Hyundai', 'Kia', 'Dacia',
                 'Mini', 'Jeep', 'Land Rover', 'Porsche', 'Tesla', 'Alfa Romeo']
        
        title_upper = title.upper()
        brand = ""
        model = ""
        
        for b in brands:
            if b.upper() in title_upper:
                brand = b
                # Try to extract model (word after brand)
                pattern = rf"{b}\s+([A-Za-z0-9\-]+)"
                match = re.search(pattern, title, re.IGNORECASE)
                if match:
                    model = match.group(1)
                break
        
        return brand, model
    
    def _extract_year(self, text):
        """Extract year from text"""
        # Look for 4-digit years between 1990 and 2026
        matches = re.findall(r'\b(19[9]\d|20[0-2]\d)\b', text)
        if matches:
            year = int(matches[0])
            if 1990 <= year <= 2026:
                return year
        return None
    
    def _extract_mileage(self, text):
        """Extract mileage from text"""
        # Look for patterns like "120000 km", "120 000km", etc.
        patterns = [
            r'(\d{1,3}(?:\s?\d{3})*)\s*km',
            r'(\d+)\s*kilomètres'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                km_str = matches[0].replace(' ', '').replace('.', '')
                try:
                    km = int(km_str)
                    if 0 <= km <= 500000:  # Reasonable range
                        return km
                except:
                    pass
        return None
    
    def _extract_price(self, price_text):
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove spaces and extract number
        price_clean = price_text.replace(' ', '').replace('€', '').replace(',', '.')
        matches = re.findall(r'(\d+(?:\.\d+)?)', price_clean)
        if matches:
            try:
                price = float(matches[0])
                if 500 <= price <= 200000:  # Reasonable car price range
                    return int(price)
            except:
                pass
        return None
    
    def _extract_fuel(self, text):
        """Extract fuel type from text"""
        fuel_map = {
            'essence': 'Essence',
            'diesel': 'Diesel',
            'électrique': 'Électrique',
            'electrique': 'Électrique',
            'hybride': 'Hybride',
            'gpl': 'GPL',
            'hdi': 'Diesel',  # HDI = diesel
            'dti': 'Diesel',  # DTI = diesel
            'tdi': 'Diesel',  # TDI = diesel
        }
        
        text_lower = text.lower()
        for keyword, fuel_type in fuel_map.items():
            if keyword in text_lower:
                return fuel_type
        
        return ""
    
    def _go_to_next_page(self, page):
        """Try to navigate to next page"""
        try:
            # Look for "next" button or pagination
            next_selectors = [
                'button:has-text("En voir plus")',
                'button:has-text("Suivant")',
                'a:has-text("Suivant")',
                '[aria-label*="Next"]'
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = page.locator(selector).first
                    if next_btn.count() > 0 and next_btn.is_visible():
                        next_btn.click()
                        time.sleep(3)
                        return True
                except:
                    continue
            
            self.logger.info("No more pages available")
            return False
            
        except Exception as e:
            self.logger.debug(f"Error going to next page: {e}")
            return False
    
    def export_to_csv(self, filename=None):
        """Export results to CSV"""
        if not self.cars:
            print("⚠️  No data to export")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/topannonces_cars_{timestamp}.csv"
        
        # Ensure output directory exists
        import os
        os.makedirs('output', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.cars[0].keys())
            writer.writeheader()
            writer.writerows(self.cars)
        
        print(f"\n✅ Exported {len(self.cars)} cars to {filename}")

if __name__ == "__main__":
    print("="*70)
    print("TOPANNONCES.FR CAR SCRAPER - REAL DATA EXTRACTION")
    print("="*70)
    print("Scraping actual car listings from TopAnnonces.fr")
    print("✅ No CAPTCHA protection - Production ready!")
    print("="*70)
    
    scraper = TopAnnoncesScraper(max_results=50, headless=True)
    cars = scraper.scrape_cars()
    
    if cars:
        scraper.export_to_csv()
        
        # Display sample
        print(f"\n📊 Sample of extracted data (first 3 cars):")
        print("-" * 70)
        for i, car in enumerate(cars[:3], 1):
            print(f"\n{i}. {car['title']}")
            print(f"   Brand: {car['brand']}, Model: {car['model']}")
            print(f"   Year: {car['year']}, Price: {car['price']}")
            print(f"   Location: {car['location']}")
            print(f"   URL: {car['url']}")
    else:
        print("\n⚠️  No data extracted")
        print("Check the logs above for details.")