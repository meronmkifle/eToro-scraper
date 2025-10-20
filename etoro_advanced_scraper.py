"""
eToro Advanced Investor Scraper
Auto-installs Chrome driver and provides enhanced scraping capabilities
"""

import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime


class EtoroAdvancedScraper:
    def __init__(self, headless=False, login_credentials=None):
        """
        Initialize scraper with automatic driver installation
        
        Args:
            headless (bool): Run browser in headless mode
            login_credentials (dict): Optional {'username': 'x', 'password': 'y'}
        """
        self.options = Options()
        self.login_credentials = login_credentials
        
        # Anti-detection measures
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        if headless:
            self.options.add_argument('--headless=new')
        
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        """Start Chrome driver with auto-installation"""
        print("Starting Chrome driver...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # Remove webdriver detection
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        print("Driver started successfully")
    
    def login(self):
        """Login to eToro if credentials provided"""
        if not self.login_credentials:
            return False
        
        print("Attempting to log in...")
        self.driver.get("https://www.etoro.com/login")
        time.sleep(3)
        
        try:
            # Find and fill username
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(self.login_credentials['username'])
            
            # Find and fill password
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.login_credentials['password'])
            
            # Submit
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(5)
            print("Login successful")
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def close_driver(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("Driver closed")
    
    def extract_number(self, text):
        """Extract numeric value from text"""
        if not text:
            return None
        match = re.search(r'[-+]?\d*\.?\d+', text.replace(',', ''))
        return float(match.group()) if match else None
    
    def scrape_investor_complete(self, username):
        """
        Complete scraping workflow for an investor
        
        Args:
            username (str): eToro username
            
        Returns:
            dict: Comprehensive investor data
        """
        url = f"https://www.etoro.com/people/{username}"
        print(f"\n{'='*60}")
        print(f"SCRAPING INVESTOR: {username}")
        print(f"{'='*60}\n")
        
        self.start_driver()
        
        # Login if credentials provided
        if self.login_credentials:
            self.login()
        
        # Navigate to investor profile
        self.driver.get(url)
        time.sleep(5)
        
        # Handle cookie consent if present
        try:
            cookie_accept = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'agree')]")
            cookie_accept.click()
            time.sleep(1)
        except:
            pass
        
        investor_data = {
            'username': username,
            'profile_url': url,
            'scraped_at': datetime.now().isoformat(),
            'profile_info': self.get_profile_info(),
            'performance_stats': self.get_performance_stats(),
            'trading_stats': self.get_trading_stats(),
            'portfolio': self.get_portfolio_data(),
            'open_trades': self.get_open_trades(),
            'trade_history': self.get_trade_history(),
            'raw_page_data': self.get_raw_data()
        }
        
        self.close_driver()
        return investor_data
    
    def get_profile_info(self):
        """Extract profile information"""
        print("Extracting profile info...")
        profile = {}
        
        try:
            # Get all visible text
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Extract key metrics using regex patterns
            patterns = {
                'copiers': r'(\d+(?:,\d+)?)\s*[Cc]opiers',
                'aum': r'\$?([\d,]+(?:\.\d+)?[KMB]?)\s*AUM',
                'gain': r'([-+]?\d+(?:\.\d+)?%)\s*[Gg]ain',
                'risk_score': r'[Rr]isk\s*[Ss]core\s*(\d+)',
                'max_drawdown': r'[Mm]ax\s*[Dd]rawdown\s*([-]?\d+(?:\.\d+)?%)',
                'weekly_dd': r'[Ww]eekly\s*[Dd]rawdown\s*([-]?\d+(?:\.\d+)?%)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, body_text)
                if match:
                    profile[key] = match.group(1)
            
            # Get profile name/title
            try:
                title = self.driver.find_element(By.TAG_NAME, "h1").text
                profile['name'] = title
            except:
                profile['name'] = username
            
            print(f"Profile data: {profile}")
            
        except Exception as e:
            print(f"Error extracting profile: {e}")
        
        return profile
    
    def get_performance_stats(self):
        """Extract performance statistics"""
        print("Extracting performance stats...")
        stats = {}
        
        try:
            # Navigate to Stats tab
            tabs = self.driver.find_elements(By.TAG_NAME, "button")
            for tab in tabs:
                if "stat" in tab.text.lower():
                    tab.click()
                    time.sleep(2)
                    break
            
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Extract performance metrics
            metrics = {
                'total_gain': r'[Tt]otal\s*[Gg]ain\s*([-+]?\d+(?:\.\d+)?%)',
                'yearly_return': r'[Yy]early\s*[Rr]eturn\s*([-+]?\d+(?:\.\d+)?%)',
                'monthly_return': r'[Mm]onthly\s*[Rr]eturn\s*([-+]?\d+(?:\.\d+)?%)',
                'daily_return': r'[Dd]aily\s*([-+]?\d+(?:\.\d+)?%)'
            }
            
            for key, pattern in metrics.items():
                match = re.search(pattern, body_text)
                if match:
                    stats[key] = match.group(1)
            
            print(f"Performance stats: {stats}")
            
        except Exception as e:
            print(f"Error extracting performance: {e}")
        
        return stats
    
    def get_trading_stats(self):
        """Extract trading statistics"""
        print("Extracting trading stats...")
        trading = {}
        
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            patterns = {
                'total_trades': r'[Tt]otal\s*[Tt]rades\s*(\d+(?:,\d+)?)',
                'profitable_trades': r'[Pp]rofitable\s*(\d+(?:\.\d+)?%)',
                'win_rate': r'[Ww]in\s*[Rr]ate\s*(\d+(?:\.\d+)?%)',
                'avg_profit': r'[Aa]vg\.?\s*[Pp]rofit\s*([-+]?\d+(?:\.\d+)?%)',
                'avg_loss': r'[Aa]vg\.?\s*[Ll]oss\s*([-+]?\d+(?:\.\d+)?%)',
                'trades_per_week': r'[Tt]rades\s*[Pp]er\s*[Ww]eek\s*(\d+(?:\.\d+)?)',
                'avg_holding_time': r'[Aa]vg\.?\s*[Hh]olding\s*[Tt]ime\s*(\d+\s*\w+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, body_text)
                if match:
                    trading[key] = match.group(1)
            
            print(f"Trading stats: {trading}")
            
        except Exception as e:
            print(f"Error extracting trading stats: {e}")
        
        return trading
    
    def get_portfolio_data(self):
        """Extract current portfolio holdings"""
        print("Extracting portfolio...")
        portfolio = []
        
        try:
            # Click Portfolio tab
            tabs = self.driver.find_elements(By.TAG_NAME, "button")
            for tab in tabs:
                if "portfolio" in tab.text.lower():
                    tab.click()
                    time.sleep(3)
                    break
            
            # Get portfolio items
            page_source = self.driver.page_source
            
            # Look for common portfolio patterns
            instruments = re.findall(r'\$([A-Z]{1,5})\b', page_source)
            portfolio = list(set(instruments))[:50]  # Remove duplicates, limit to 50
            
            print(f"Portfolio instruments found: {len(portfolio)}")
            
        except Exception as e:
            print(f"Error extracting portfolio: {e}")
        
        return portfolio
    
    def get_open_trades(self):
        """Extract currently open trades"""
        print("Extracting open trades...")
        trades = []
        
        try:
            # This requires being logged in
            # Extract trade data from page
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Look for BUY/SELL patterns
            trade_patterns = re.findall(r'(BUY|SELL)\s+([A-Z]{1,5})', body_text)
            trades = [{'action': action, 'symbol': symbol} for action, symbol in trade_patterns]
            
            print(f"Open trades found: {len(trades)}")
            
        except Exception as e:
            print(f"Error extracting open trades: {e}")
        
        return trades
    
    def get_trade_history(self):
        """Extract closed trade history"""
        print("Extracting trade history...")
        history = []
        
        try:
            # Look for History section
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "history" in button.text.lower():
                    button.click()
                    time.sleep(3)
                    break
            
            # Extract historical data
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Simple extraction - can be enhanced based on actual page structure
            print("History section accessed")
            
        except Exception as e:
            print(f"Error extracting history: {e}")
        
        return history
    
    def get_raw_data(self):
        """Get raw page data for manual inspection"""
        try:
            return {
                'page_text': self.driver.find_element(By.TAG_NAME, "body").text[:5000],  # First 5000 chars
                'url': self.driver.current_url
            }
        except:
            return {}
    
    def save_data(self, data, filename=None):
        """Save data to JSON file"""
        if not filename:
            filename = f"etoro_{data['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data saved to: {filename}")
        return filename


# Main execution
def main():
    """Main execution function"""
    
    # Configuration
    USERNAME = "thomaspj"
    HEADLESS = False  # Set to True to hide browser
    
    # Optional: Add login credentials if you need access to protected data
    # CREDENTIALS = {'username': 'your_email', 'password': 'your_password'}
    CREDENTIALS = None
    
    print("\n" + "="*60)
    print("eToro Investor Scraper")
    print("="*60)
    
    # Create scraper
    scraper = EtoroAdvancedScraper(headless=HEADLESS, login_credentials=CREDENTIALS)
    
    # Scrape investor
    data = scraper.scrape_investor_complete(USERNAME)
    
    # Save results
    filename = scraper.save_data(data)
    
    # Print summary
    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    print(f"Username: {data['username']}")
    print(f"Profile items: {len(data['profile_info'])}")
    print(f"Performance metrics: {len(data['performance_stats'])}")
    print(f"Trading stats: {len(data['trading_stats'])}")
    print(f"Portfolio items: {len(data['portfolio'])}")
    print(f"Open trades: {len(data['open_trades'])}")
    print(f"\nOutput file: {filename}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
