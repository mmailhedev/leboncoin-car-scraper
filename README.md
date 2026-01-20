# TopAnnonces.fr Car Scraper

🚗 **Production-ready web scraper** for extracting real car listings from TopAnnonces.fr using Playwright.

## ✨ Features

- ✅ **No CAPTCHA** - Direct scraping without protection
- 🎯 **Accurate data extraction** - Brand, model, year, price, mileage, fuel type
- 📊 **CSV export** - Clean, structured data output
- 🔄 **Smart pagination** - Automatic page navigation
- 🛡️ **Error handling** - Robust scraping with proper logging
- 🚀 **Fast & efficient** - Optimized for production use

## 📋 Data Extracted

Each car listing includes:
- Title
- Brand & Model
- Year
- Price (text + numeric)
- Mileage (km)
- Fuel type (Essence, Diesel, Électrique, Hybride, GPL)
- Location
- Description
- Direct URL to listing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/topannonces-scraper.git
cd topannonces-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

### Usage

Run the scraper:
```bash
python scraper.py
```

The script will:
1. Scrape 50 car listings from TopAnnonces.fr
2. Export results to `output/topannonces_cars_YYYYMMDD_HHMMSS.csv`
3. Display a sample of extracted data

### Customization

```python
from scraper import TopAnnoncesScraper

# Custom configuration
scraper = TopAnnoncesScraper(
    max_results=100,    # Number of listings to scrape
    headless=True       # Run in headless mode (False to see browser)
)

cars = scraper.scrape_cars()
scraper.export_to_csv('my_cars.csv')
```

## 📁 Project Structure

```
topannonces-scraper/
├── scraper.py           # Main scraper class
├── requirements.txt     # Python dependencies
├── README.md           # Documentation
├── output/             # CSV exports (auto-created)
└── .gitignore         # Git ignore rules
```

## 🛠️ Technical Details

### Technologies Used

- **Playwright** - Browser automation and web scraping
- **Python 3.8+** - Core language
- **CSV** - Data export format

### How It Works

1. **Navigation** - Opens TopAnnonces.fr vehicle section
2. **Cookie handling** - Accepts cookies automatically
3. **Card detection** - Finds Angular Material card elements
4. **Data extraction** - Parses title, price, location, description
5. **Smart filtering** - Keeps only car-related listings
6. **Pagination** - Navigates through multiple pages
7. **Export** - Saves to timestamped CSV file

### Data Processing

The scraper intelligently extracts:
- **Brand/Model** - From 25+ known car brands
- **Year** - 4-digit years (1990-2026)
- **Mileage** - Various formats (120000 km, 120 000km)
- **Price** - Numeric values (€500-€200,000 range)
- **Fuel type** - Maps keywords (HDI→Diesel, etc.)

## 📊 Output Example

```csv
title,brand,model,year,mileage,price,price_numeric,fuel_type,location,description,url
Renault Clio IV,Renault,Clio,2018,85000,9 500 €,9500,Diesel,Montpellier,"Renault Clio IV 1.5 dCi, bon état...",https://www.topannonces.fr/...
```

## ⚙️ Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_results` | int | 50 | Maximum listings to scrape |
| `headless` | bool | True | Run browser in headless mode |

## 🔧 Troubleshooting

**No data extracted?**
- Check internet connection
- Verify TopAnnonces.fr is accessible
- Run with `headless=False` to see what's happening

**Missing data fields?**
- Some listings may not have all fields
- Check logs for extraction errors

**Playwright errors?**
```bash
# Reinstall browsers
playwright install chromium --force
```

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## ⚠️ Disclaimer

This scraper is for educational purposes. Always:
- Respect TopAnnonces.fr's terms of service
- Don't overload their servers
- Use responsibly and ethically

## 📧 Contact

Questions or issues? Open a GitHub issue or contact me.

---

**Happy scraping!** 🚗💨
