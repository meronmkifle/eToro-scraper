# eToro Investor Scraper

A Python-based web scraper for extracting investor data from eToro profiles, including stats, portfolio, and trade history.

## Features

- ✅ Scrapes investor profile information (copiers, AUM, risk score)
- ✅ Extracts performance statistics (gain, returns, drawdown)
- ✅ Captures trading statistics (win rate, total trades, avg profit/loss)
- ✅ Gets portfolio holdings
- ✅ Retrieves open trades and trade history
- ✅ Auto-installs Chrome driver
- ✅ Anti-detection measures
- ✅ Exports data to JSON

## Installation

### 1. Install Python
Make sure you have Python 3.8+ installed.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install selenium webdriver-manager beautifulsoup4 requests
```

### 3. Install Chrome Browser
Make sure Google Chrome is installed on your system.

## Usage

### Basic Usage

```python
from etoro_advanced_scraper import EtoroAdvancedScraper

# Create scraper
scraper = EtoroAdvancedScraper(headless=False)

# Scrape investor
data = scraper.scrape_investor_complete("thomaspj")

# Save to JSON
scraper.save_data(data)
```

### Run the Script

Simply execute the script:
```bash
python etoro_advanced_scraper.py
```

The script will:
1. Open Chrome browser
2. Navigate to the investor's profile
3. Extract all available data
4. Save results to a JSON file

### Command Line Options

Modify these variables in the script:

```python
USERNAME = "thomaspj"  # Change to any eToro username
HEADLESS = False       # Set to True to hide browser
```

### With Login (Optional)

If you need to access protected data:

```python
CREDENTIALS = {
    'username': 'your_email@example.com',
    'password': 'your_password'
}

scraper = EtoroAdvancedScraper(
    headless=False,
    login_credentials=CREDENTIALS
)
```

## Output Format

The scraper generates a JSON file with this structure:

```json
{
  "username": "thomaspj",
  "profile_url": "https://www.etoro.com/people/thomaspj",
  "scraped_at": "2025-10-20T12:30:00",
  "profile_info": {
    "name": "Thomas PJ",
    "copiers": "1,234",
    "aum": "$5.2M",
    "gain": "+125.5%",
    "risk_score": "4"
  },
  "performance_stats": {
    "total_gain": "+125.5%",
    "yearly_return": "+45.2%",
    "monthly_return": "+3.8%"
  },
  "trading_stats": {
    "total_trades": "523",
    "win_rate": "78.5%",
    "avg_profit": "+5.2%",
    "avg_loss": "-2.1%",
    "trades_per_week": "4.5"
  },
  "portfolio": ["AAPL", "GOOGL", "TSLA", "BTC"],
  "open_trades": [],
  "trade_history": []
}
```

## Important Notes

### Legal Disclaimer
⚠️ **This scraper is for educational purposes only.**
- Respect eToro's Terms of Service
- Use responsibly and don't overload their servers
- Don't use scraped data for commercial purposes without permission

### Limitations
- eToro heavily uses JavaScript, so some data may not be accessible without login
- The site structure may change, requiring updates to selectors
- Rate limiting may apply
- Some data requires authentication

### Troubleshooting

**Chrome driver issues:**
- The script auto-downloads the correct Chrome driver
- Make sure Chrome browser is installed

**No data scraped:**
- Try running with `HEADLESS = False` to see what's happening
- Some data may require login
- eToro's page structure may have changed

**Bot detection:**
- The script includes anti-detection measures
- If detected, try adding random delays
- Consider using proxies for multiple requests

## Customization

### Add More Data Points

Edit the regex patterns in the scraper methods:

```python
patterns = {
    'your_metric': r'Your\s*Pattern\s*(\d+)',
}
```

### Change Timeout/Delays

Adjust sleep times in the code:
```python
time.sleep(5)  # Increase if page loads slowly
```

## Advanced Features

### Scrape Multiple Investors

```python
investors = ["thomaspj", "investor2", "investor3"]

for username in investors:
    data = scraper.scrape_investor_complete(username)
    scraper.save_data(data)
    time.sleep(10)  # Be nice to the server
```

### Export to CSV

```python
import pandas as pd

# Convert JSON to DataFrame
df = pd.DataFrame([data])
df.to_csv('etoro_data.csv', index=False)
```

## Contributing

Feel free to improve the scraper:
- Add more data extraction patterns
- Improve error handling
- Add export formats (CSV, Excel)
- Enhance anti-detection measures

## License

MIT License - Use at your own risk

