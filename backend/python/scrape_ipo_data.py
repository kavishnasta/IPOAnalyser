import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import json
from datetime import datetime
from urllib.parse import urljoin, quote
import csv

class IndianIPODataScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.ipo_data = []

    def extract_number(self, text):
        if not text:
            return None
        text = str(text).replace(',', '').replace('₹', '').replace('Rs.', '').replace('Rs', '')
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            num = float(numbers[0])
            if 'lakh' in text.lower():
                num = num * 0.01
            elif 'thousand' in text.lower():
                num = num * 0.0001
            return num
        return None

    def extract_percentage(self, text):
        if not text:
            return None
        text = str(text)
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            return float(numbers[0]) / 100.0 if '%' not in text else float(numbers[0])
        return None

    def scrape_moneycontrol_ipos(self):
        try:
            url = 'https://www.moneycontrol.com/ipo/ipo-historic-data'
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 8:
                            try:
                                company_name = cols[0].get_text(strip=True)
                                symbol = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                                issue_size_text = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                                listing_date_text = cols[3].get_text(strip=True) if len(cols) > 3 else ''
                                listing_price_text = cols[4].get_text(strip=True) if len(cols) > 4 else ''
                                listing_gain_text = cols[5].get_text(strip=True) if len(cols) > 5 else ''
                                
                                issue_size = self.extract_number(issue_size_text)
                                listing_gain = self.extract_number(listing_gain_text)
                                
                                if company_name and issue_size:
                                    ipo_record = {
                                        'Company_Name': company_name,
                                        'Symbol': symbol,
                                        'Issue_Size': issue_size,
                                        'QIB_Subscription': None,
                                        'HNI_Subscription': None,
                                        'Retail_Subscription': None,
                                        'PE_Ratio': None,
                                        'OFS_Percentage': None,
                                        'GMP_Listing_Day': listing_gain if listing_gain else 0,
                                        'Positive_Listing_Gain': listing_gain > 0 if listing_gain else False,
                                        'Sector': None
                                    }
                                    self.ipo_data.append(ipo_record)
                            except Exception as e:
                                continue
            time.sleep(2)
        except Exception as e:
            pass

    def scrape_chittorgarh_ipos(self):
        try:
            url = 'https://www.chittorgarh.com/report/ipo-historical-data/2/'
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', class_='table')
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 10:
                            try:
                                company_name = cols[0].get_text(strip=True)
                                symbol = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                                issue_size_text = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                                qib_text = cols[3].get_text(strip=True) if len(cols) > 3 else ''
                                hni_text = cols[4].get_text(strip=True) if len(cols) > 4 else ''
                                retail_text = cols[5].get_text(strip=True) if len(cols) > 5 else ''
                                listing_gain_text = cols[6].get_text(strip=True) if len(cols) > 6 else ''
                                
                                issue_size = self.extract_number(issue_size_text)
                                qib_sub = self.extract_number(qib_text)
                                hni_sub = self.extract_number(hni_text)
                                retail_sub = self.extract_number(retail_text)
                                listing_gain = self.extract_number(listing_gain_text)
                                
                                if company_name and issue_size:
                                    ipo_record = {
                                        'Company_Name': company_name,
                                        'Symbol': symbol,
                                        'Issue_Size': issue_size,
                                        'QIB_Subscription': qib_sub if qib_sub else 1.0,
                                        'HNI_Subscription': hni_sub if hni_sub else 1.0,
                                        'Retail_Subscription': retail_sub if retail_sub else 1.0,
                                        'PE_Ratio': None,
                                        'OFS_Percentage': None,
                                        'GMP_Listing_Day': listing_gain if listing_gain else 0,
                                        'Positive_Listing_Gain': listing_gain > 0 if listing_gain else False,
                                        'Sector': None
                                    }
                                    self.ipo_data.append(ipo_record)
                            except Exception as e:
                                continue
            time.sleep(2)
        except Exception as e:
            pass

    def scrape_ipo_watch(self):
        try:
            url = 'https://ipowatch.in/ipo-list/'
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                ipo_cards = soup.find_all('div', class_='ipo-card') or soup.find_all('div', class_='ipo-item')
                for card in ipo_cards:
                    try:
                        company_name_elem = card.find('h3') or card.find('h2') or card.find('a')
                        if company_name_elem:
                            company_name = company_name_elem.get_text(strip=True)
                            details = card.find_all('span') or card.find_all('div', class_='detail')
                            
                            issue_size = None
                            qib_sub = None
                            hni_sub = None
                            retail_sub = None
                            listing_gain = None
                            
                            for detail in details:
                                text = detail.get_text(strip=True)
                                if 'issue size' in text.lower() or 'size' in text.lower():
                                    issue_size = self.extract_number(text)
                                elif 'qib' in text.lower():
                                    qib_sub = self.extract_number(text)
                                elif 'hni' in text.lower() or 'nii' in text.lower():
                                    hni_sub = self.extract_number(text)
                                elif 'retail' in text.lower():
                                    retail_sub = self.extract_number(text)
                                elif 'listing' in text.lower() or 'gain' in text.lower():
                                    listing_gain = self.extract_number(text)
                            
                            if company_name and issue_size:
                                ipo_record = {
                                    'Company_Name': company_name,
                                    'Symbol': '',
                                    'Issue_Size': issue_size,
                                    'QIB_Subscription': qib_sub if qib_sub else 1.0,
                                    'HNI_Subscription': hni_sub if hni_sub else 1.0,
                                    'Retail_Subscription': retail_sub if retail_sub else 1.0,
                                    'PE_Ratio': None,
                                    'OFS_Percentage': None,
                                    'GMP_Listing_Day': listing_gain if listing_gain else 0,
                                    'Positive_Listing_Gain': listing_gain > 0 if listing_gain else False,
                                    'Sector': None
                                }
                                self.ipo_data.append(ipo_record)
                    except Exception as e:
                        continue
            time.sleep(2)
        except Exception as e:
            pass

    def scrape_nse_ipo_data(self):
        try:
            url = 'https://www.nseindia.com/api/ipo-historical-data'
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        try:
                            company_name = item.get('companyName', '')
                            symbol = item.get('symbol', '')
                            issue_size = item.get('issueSize', 0)
                            qib_sub = item.get('qibSubscription', 1.0)
                            hni_sub = item.get('hniSubscription', 1.0)
                            retail_sub = item.get('retailSubscription', 1.0)
                            listing_gain = item.get('listingGain', 0)
                            
                            if company_name:
                                ipo_record = {
                                    'Company_Name': company_name,
                                    'Symbol': symbol,
                                    'Issue_Size': issue_size,
                                    'QIB_Subscription': qib_sub if qib_sub else 1.0,
                                    'HNI_Subscription': hni_sub if hni_sub else 1.0,
                                    'Retail_Subscription': retail_sub if retail_sub else 1.0,
                                    'PE_Ratio': item.get('peRatio'),
                                    'OFS_Percentage': item.get('ofsPercentage'),
                                    'GMP_Listing_Day': listing_gain if listing_gain else 0,
                                    'Positive_Listing_Gain': listing_gain > 0 if listing_gain else False,
                                    'Sector': item.get('sector')
                                }
                                self.ipo_data.append(ipo_record)
                        except Exception as e:
                            continue
            time.sleep(2)
        except Exception as e:
            pass

    def scrape_5paisa_ipos(self):
        try:
            url = 'https://www.5paisa.com/ipo/ipo-historical-data'
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 7:
                            try:
                                company_name = cols[0].get_text(strip=True)
                                symbol = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                                issue_size_text = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                                listing_gain_text = cols[3].get_text(strip=True) if len(cols) > 3 else ''
                                
                                issue_size = self.extract_number(issue_size_text)
                                listing_gain = self.extract_number(listing_gain_text)
                                
                                if company_name and issue_size:
                                    ipo_record = {
                                        'Company_Name': company_name,
                                        'Symbol': symbol,
                                        'Issue_Size': issue_size,
                                        'QIB_Subscription': None,
                                        'HNI_Subscription': None,
                                        'Retail_Subscription': None,
                                        'PE_Ratio': None,
                                        'OFS_Percentage': None,
                                        'GMP_Listing_Day': listing_gain if listing_gain else 0,
                                        'Positive_Listing_Gain': listing_gain > 0 if listing_gain else False,
                                        'Sector': None
                                    }
                                    self.ipo_data.append(ipo_record)
                            except Exception as e:
                                continue
            time.sleep(2)
        except Exception as e:
            pass

    def enrich_ipo_details(self, ipo_record):
        try:
            company_name = ipo_record.get('Company_Name', '')
            if not company_name:
                return ipo_record
            
            search_query = f"{company_name} IPO India PE ratio OFS"
            url = f"https://www.google.com/search?q={quote(search_query)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                if ipo_record.get('PE_Ratio') is None:
                    pe_match = re.search(r'P/E[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
                    if pe_match:
                        ipo_record['PE_Ratio'] = float(pe_match.group(1))
                
                if ipo_record.get('OFS_Percentage') is None:
                    ofs_match = re.search(r'OFS[:\s]+(\d+\.?\d*)%', text, re.IGNORECASE)
                    if ofs_match:
                        ipo_record['OFS_Percentage'] = float(ofs_match.group(1)) / 100.0
                
                if not ipo_record.get('Sector'):
                    sector_match = re.search(r'Sector[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
                    if sector_match:
                        ipo_record['Sector'] = sector_match.group(1).strip()
            
            time.sleep(1)
        except Exception as e:
            pass
        
        return ipo_record

    def scrape_all_sources(self):
        print("Starting IPO data scraping from multiple sources...")
        print("Scraping Moneycontrol...")
        self.scrape_moneycontrol_ipos()
        print(f"Collected {len(self.ipo_data)} IPOs so far...")
        
        print("Scraping Chittorgarh...")
        self.scrape_chittorgarh_ipos()
        print(f"Collected {len(self.ipo_data)} IPOs so far...")
        
        print("Scraping IPO Watch...")
        self.scrape_ipo_watch()
        print(f"Collected {len(self.ipo_data)} IPOs so far...")
        
        print("Scraping NSE...")
        self.scrape_nse_ipo_data()
        print(f"Collected {len(self.ipo_data)} IPOs so far...")
        
        print("Scraping 5paisa...")
        self.scrape_5paisa_ipos()
        print(f"Collected {len(self.ipo_data)} IPOs so far...")
        
        print("Enriching IPO details...")
        for i, ipo in enumerate(self.ipo_data):
            if i % 10 == 0:
                print(f"Enriching {i+1}/{len(self.ipo_data)}...")
            self.ipo_data[i] = self.enrich_ipo_details(ipo)
            time.sleep(0.5)

    def clean_and_deduplicate(self):
        seen = set()
        cleaned_data = []
        for ipo in self.ipo_data:
            key = (ipo.get('Company_Name', '').lower().strip(), ipo.get('Symbol', '').upper().strip())
            if key not in seen and key[0]:
                seen.add(key)
                if ipo.get('Issue_Size') and ipo.get('Issue_Size') > 0:
                    if ipo.get('QIB_Subscription') is None:
                        ipo['QIB_Subscription'] = 1.0
                    if ipo.get('HNI_Subscription') is None:
                        ipo['HNI_Subscription'] = 1.0
                    if ipo.get('Retail_Subscription') is None:
                        ipo['Retail_Subscription'] = 1.0
                    if ipo.get('PE_Ratio') is None:
                        ipo['PE_Ratio'] = 20.0
                    if ipo.get('OFS_Percentage') is None:
                        ipo['OFS_Percentage'] = 0.5
                    cleaned_data.append(ipo)
        self.ipo_data = cleaned_data

    def save_to_csv(self, filename='indian_ipo_data.csv'):
        if not self.ipo_data:
            print("No IPO data collected.")
            return
        
        self.clean_and_deduplicate()
        
        df = pd.DataFrame(self.ipo_data)
        df = df[[
            'Company_Name', 'Symbol', 'Issue_Size', 'QIB_Subscription',
            'HNI_Subscription', 'Retail_Subscription', 'PE_Ratio',
            'OFS_Percentage', 'GMP_Listing_Day', 'Positive_Listing_Gain', 'Sector'
        ]]
        
        df.to_csv(filename, index=False)
        print(f"\nSaved {len(df)} IPO records to {filename}")
        print(f"\nData Summary:")
        print(df.describe())
        return filename

if __name__ == '__main__':
    scraper = IndianIPODataScraper()
    scraper.scrape_all_sources()
    scraper.save_to_csv('indian_ipo_data.csv')
