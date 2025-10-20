"""
eToro Investor Profile Scraper
Scrapes investor stats, portfolio, and trade history from eToro profiles
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime


class EtoroInvestorScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome options"""
        self.options = Options()
        
        # Stealth options to avoid detection
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if headless:
            self.options.add_argument('--headless')
        
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        """Start the Chrome driver"""
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # Execute script to remove webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def close_driver(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
    
    def scrape_investor(self, username):
        """
        Scrape all data for a specific investor
        
        Args:
            username (str): eToro username (e.g., 'thomaspj')
            
        Returns:
            dict: Complete investor data
        """
        url = f"https://www.etoro.com/people/{username}"
        
        print(f"Scraping investor: {username}")
        print(f"URL: {url}")
        
        self.start_driver()
        self.driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        investor_data = {
            'username': username,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'profile': {},
            'stats': {},
            'portfolio': [],
            'trade_history': []
        }
        
        try:
            # Scrape profile information
            investor_data['profile'] = self.scrape_profile()
            
            # Scrape stats
            investor_data['stats'] = self.scrape_stats()
            
            # Scrape portfolio
            investor_data['portfolio'] = self.scrape_portfolio()
            
            # Scrape trade history
            investor_data['trade_history'] = self.scrape_trade_history()
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            investor_data['error'] = str(e)
        
        finally:
            self.close_driver()
        
        return investor_data
    
    def scrape_profile(self):
        """Scrape basic profile information"""
        profile_data = {}
        
        try:
            # Try to get profile name
            try:
                name_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, [data-etoro-automation-id='user-name']"))
                )
                profile_data['name'] = name_element.text
            except:
                profile_data['name'] = 'N/A'
            
            # Get copy traders (followers)
            try:
                copiers = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Copiers')]")
                profile_data['copiers'] = copiers.text
            except:
                profile_data['copiers'] = 'N/A'
            
            # Get risk score
            try:
                risk_score = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Risk Score')]")
                profile_data['risk_score'] = risk_score.text
            except:
                profile_data['risk_score'] = 'N/A'
            
            print(f"Profile scraped: {profile_data}")
            
        except Exception as e:
            print(f"Error scraping profile: {e}")
        
        return profile_data
    
    def scrape_stats(self):
        """Scrape statistics and performance data"""
        stats_data = {
            'performance': {},
            'trades': {},
            'additional': {}
        }
        
        try:
            # Click on Stats tab if available
            try:
                stats_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Stats')]")
                stats_tab.click()
                time.sleep(2)
            except:
                print("Stats tab not found, continuing with current view")
            
            # Get all text content for parsing
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Parse performance metrics
            if "Gain" in page_text:
                try:
                    gain = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Gain')]/following-sibling::*")
                    stats_data['performance']['gain'] = gain.text
                except:
                    pass
            
            # Parse trading stats
            if "Total Trades" in page_text or "trades" in page_text.lower():
                try:
                    trades = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Trades')]")
                    stats_data['trades']['total'] = trades.text
                except:
                    pass
            
            # Get win rate
            if "Win Rate" in page_text or "Profitable" in page_text:
                try:
                    win_rate = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Win') or contains(text(), 'Profitable')]")
                    stats_data['trades']['win_rate'] = win_rate.text
                except:
                    pass
            
            print(f"Stats scraped: {stats_data}")
            
        except Exception as e:
            print(f"Error scraping stats: {e}")
        
        return stats_data
    
    def scrape_portfolio(self):
        """Scrape current portfolio holdings"""
        portfolio = []
        
        try:
            # Click on Portfolio tab
            try:
                portfolio_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Portfolio')]")
                portfolio_tab.click()
                time.sleep(3)
            except:
                print("Portfolio tab not found")
                return portfolio
            
            # Find all portfolio items
            try:
                portfolio_items = self.driver.find_elements(By.CSS_SELECTOR, "[class*='portfolio'], [class*='position'], [data-etoro-automation-id*='portfolio']")
                
                for item in portfolio_items[:10]:  # Limit to first 10 to avoid timeout
                    try:
                        item_data = {
                            'text': item.text,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Try to extract ticker/symbol
                        if item.text and len(item.text) > 0:
                            portfolio.append(item_data)
                    except:
                        continue
                
                print(f"Portfolio items found: {len(portfolio)}")
                
            except Exception as e:
                print(f"Error finding portfolio items: {e}")
        
        except Exception as e:
            print(f"Error scraping portfolio: {e}")
        
        return portfolio
    
    def scrape_trade_history(self):
        """Scrape trade history (closed positions)"""
        history = []
        
        try:
            # Click on History tab or look for history section
            try:
                history_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'History')] | //*[contains(text(), 'History')]")
                history_button.click()
                time.sleep(3)
            except:
                print("History section not directly accessible")
            
            # Try to find trade history elements
            try:
                # Look for any elements that might contain trade data
                trade_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='trade'], [class*='position'], [class*='history']")
                
                for trade in trade_elements[:20]:  # Limit to first 20
                    try:
                        if trade.text and len(trade.text) > 0:
                            trade_data = {
                                'text': trade.text,
                                'timestamp': datetime.now().isoformat()
                            }
                            history.append(trade_data)
                    except:
                        continue
                
                print(f"Trade history items found: {len(history)}")
                
            except Exception as e:
                print(f"Error finding trade elements: {e}")
        
        except Exception as e:
            print(f"Error scraping trade history: {e}")
        
        return history
    
    def save_to_json(self, data, filename):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")


# Example usage
if __name__ == "__main__":
    # Create scraper instance
    scraper = EtoroInvestorScraper(headless=False)  # Set to True to run without GUI
    
    # Scrape specific investor
    username = "thomaspj"
    data = scraper.scrape_investor(username)
    
    # Save to JSON
    filename = f"etoro_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    scraper.save_to_json(data, filename)
    
    # Print summary
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    print(f"Username: {data['username']}")
    print(f"Profile items: {len(data['profile'])}")
    print(f"Stats items: {len(data['stats'])}")
    print(f"Portfolio items: {len(data['portfolio'])}")
    print(f"Trade history items: {len(data['trade_history'])}")
    print(f"\nFull data saved to: {filename}")
