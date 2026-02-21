import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote
import csv
import random

class EnhancedIndianIPODataScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.ipo_data = []
        self.known_ipos = set()

    def extract_number(self, text):
        if not text or text == 'N/A' or text == '-':
            return None
        text = str(text).replace(',', '').replace('₹', '').replace('Rs.', '').replace('Rs', '').replace('$', '')
        text = text.replace('Crores', '').replace('crores', '').replace('Cr', '').replace('cr', '')
        text = text.replace('Lakhs', '').replace('lakhs', '').replace('L', '').replace('l', '')
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            num = float(numbers[0])
            if 'lakh' in text.lower() or 'lac' in text.lower():
                num = num * 0.01
            elif 'thousand' in text.lower():
                num = num * 0.0001
            return num
        return None

    def extract_multiplier(self, text):
        if not text or text == 'N/A' or text == '-':
            return None
        text = str(text).replace('x', '').replace('X', '').replace('times', '').strip()
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            return float(numbers[0])
        return None

    def scrape_ipo_guru(self):
        try:
            base_url = 'https://www.ipoguru.com/ipo-historical-data'
            response = self.session.get(base_url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 6:
                            try:
                                company_name = cols[0].get_text(strip=True)
                                if not company_name or company_name.lower() in ['company', 'name', 'ipo name']:
                                    continue
                                
                                symbol = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                                issue_size_text = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                                listing_gain_text = cols[3].get_text(strip=True) if len(cols) > 3 else ''
                                
                                issue_size = self.extract_number(issue_size_text)
                                listing_gain = self.extract_number(listing_gain_text)
                                
                                if company_name and issue_size and issue_size > 0:
                                    key = (company_name.lower().strip(), symbol.upper().strip())
                                    if key not in self.known_ipos:
                                        self.known_ipos.add(key)
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
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            pass

    def scrape_ipo_mania(self):
        try:
            url = 'https://www.ipomania.in/ipo-historical-data'
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                ipo_items = soup.find_all('div', class_='ipo-item') or soup.find_all('tr')
                for item in ipo_items:
                    try:
                        text = item.get_text()
                        if 'company' in text.lower() and 'size' in text.lower():
                            continue
                        
                        company_elem = item.find('a') or item.find('h3') or item.find('h2')
                        if not company_elem:
                            cols = item.find_all(['td', 'div'])
                            if len(cols) > 0:
                                company_elem = cols[0]
                        
                        if company_elem:
                            company_name = company_elem.get_text(strip=True)
                            if company_name:
                                details = item.find_all(['span', 'div', 'td'])
                                issue_size = None
                                listing_gain = None
                                
                                for detail in details:
                                    detail_text = detail.get_text(strip=True)
                                    if 'crore' in detail_text.lower() or 'cr' in detail_text.lower():
                                        issue_size = self.extract_number(detail_text)
                                    if 'listing' in detail_text.lower() or 'gain' in detail_text.lower():
                                        listing_gain = self.extract_number(detail_text)
                                
                                if company_name and issue_size and issue_size > 0:
                                    key = (company_name.lower().strip(), '')
                                    if key not in self.known_ipos:
                                        self.known_ipos.add(key)
                                        ipo_record = {
                                            'Company_Name': company_name,
                                            'Symbol': '',
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
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            pass

    def scrape_zeebiz_ipos(self):
        try:
            url = 'https://www.zeebiz.com/ipo'
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('article') or soup.find_all('div', class_='news-item')
                for article in articles:
                    try:
                        title_elem = article.find('h2') or article.find('h3') or article.find('a')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if 'IPO' in title.upper():
                                company_match = re.search(r'([A-Z][a-zA-Z\s&]+)\s+IPO', title)
                                if company_match:
                                    company_name = company_match.group(1).strip()
                                    content = article.get_text()
                                    
                                    issue_size = self.extract_number(content)
                                    listing_gain = self.extract_number(content)
                                    
                                    if company_name and issue_size and issue_size > 0:
                                        key = (company_name.lower().strip(), '')
                                        if key not in self.known_ipos:
                                            self.known_ipos.add(key)
                                            ipo_record = {
                                                'Company_Name': company_name,
                                                'Symbol': '',
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
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            pass

    def scrape_bse_ipo_data(self):
        try:
            url = 'https://www.bseindia.com/markets/PublicIssues/IPO_Issues.aspx'
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 5:
                            try:
                                company_name = cols[0].get_text(strip=True)
                                if not company_name or company_name.lower() in ['company', 'name']:
                                    continue
                                
                                symbol = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                                issue_size_text = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                                
                                issue_size = self.extract_number(issue_size_text)
                                
                                if company_name and issue_size and issue_size > 0:
                                    key = (company_name.lower().strip(), symbol.upper().strip())
                                    if key not in self.known_ipos:
                                        self.known_ipos.add(key)
                                        ipo_record = {
                                            'Company_Name': company_name,
                                            'Symbol': symbol,
                                            'Issue_Size': issue_size,
                                            'QIB_Subscription': None,
                                            'HNI_Subscription': None,
                                            'Retail_Subscription': None,
                                            'PE_Ratio': None,
                                            'OFS_Percentage': None,
                                            'GMP_Listing_Day': 0,
                                            'Positive_Listing_Gain': False,
                                            'Sector': None
                                        }
                                        self.ipo_data.append(ipo_record)
                            except Exception as e:
                                continue
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            pass

    def scrape_google_finance_data(self, company_name):
        try:
            search_query = f"{company_name} IPO India subscription QIB HNI retail"
            url = f"https://www.google.com/search?q={quote(search_query)}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                data = {}
                
                qib_match = re.search(r'QIB[:\s]+(\d+\.?\d*)\s*x', text, re.IGNORECASE)
                if qib_match:
                    data['QIB_Subscription'] = float(qib_match.group(1))
                
                hni_match = re.search(r'(?:HNI|NII)[:\s]+(\d+\.?\d*)\s*x', text, re.IGNORECASE)
                if hni_match:
                    data['HNI_Subscription'] = float(hni_match.group(1))
                
                retail_match = re.search(r'Retail[:\s]+(\d+\.?\d*)\s*x', text, re.IGNORECASE)
                if retail_match:
                    data['Retail_Subscription'] = float(retail_match.group(1))
                
                pe_match = re.search(r'P/E[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
                if pe_match:
                    data['PE_Ratio'] = float(pe_match.group(1))
                
                ofs_match = re.search(r'OFS[:\s]+(\d+\.?\d*)%', text, re.IGNORECASE)
                if ofs_match:
                    data['OFS_Percentage'] = float(ofs_match.group(1)) / 100.0
                
                sector_match = re.search(r'Sector[:\s]+([A-Za-z\s&]+)', text, re.IGNORECASE)
                if sector_match:
                    data['Sector'] = sector_match.group(1).strip()
                
                return data
        except Exception as e:
            pass
        return {}

    def enrich_with_google(self, ipo_record, index, total):
        if index % 5 == 0:
            print(f"Enriching {index+1}/{total}...")
        
        company_name = ipo_record.get('Company_Name', '')
        if not company_name:
            return ipo_record
        
        enriched_data = self.scrape_google_finance_data(company_name)
        
        if enriched_data.get('QIB_Subscription') and not ipo_record.get('QIB_Subscription'):
            ipo_record['QIB_Subscription'] = enriched_data['QIB_Subscription']
        if enriched_data.get('HNI_Subscription') and not ipo_record.get('HNI_Subscription'):
            ipo_record['HNI_Subscription'] = enriched_data['HNI_Subscription']
        if enriched_data.get('Retail_Subscription') and not ipo_record.get('Retail_Subscription'):
            ipo_record['Retail_Subscription'] = enriched_data['Retail_Subscription']
        if enriched_data.get('PE_Ratio') and not ipo_record.get('PE_Ratio'):
            ipo_record['PE_Ratio'] = enriched_data['PE_Ratio']
        if enriched_data.get('OFS_Percentage') and not ipo_record.get('OFS_Percentage'):
            ipo_record['OFS_Percentage'] = enriched_data['OFS_Percentage']
        if enriched_data.get('Sector') and not ipo_record.get('Sector'):
            ipo_record['Sector'] = enriched_data['Sector']
        
        time.sleep(random.uniform(1, 2))
        return ipo_record

    def scrape_all_sources(self):
        print("=" * 60)
        print("Enhanced Indian IPO Data Scraper")
        print("=" * 60)
        
        print("\n[1/5] Scraping IPO Guru...")
        self.scrape_ipo_guru()
        print(f"   Collected: {len(self.ipo_data)} IPOs")
        
        print("\n[2/5] Scraping IPO Mania...")
        self.scrape_ipo_mania()
        print(f"   Collected: {len(self.ipo_data)} IPOs")
        
        print("\n[3/5] Scraping Zee Business...")
        self.scrape_zeebiz_ipos()
        print(f"   Collected: {len(self.ipo_data)} IPOs")
        
        print("\n[4/5] Scraping BSE...")
        self.scrape_bse_ipo_data()
        print(f"   Collected: {len(self.ipo_data)} IPOs")
        
        print("\n[5/5] Enriching data with Google Finance...")
        total = len(self.ipo_data)
        for i in range(len(self.ipo_data)):
            self.ipo_data[i] = self.enrich_with_google(self.ipo_data[i], i, total)
        
        print(f"\nTotal unique IPOs collected: {len(self.ipo_data)}")

    def clean_and_normalize(self):
        cleaned_data = []
        for ipo in self.ipo_data:
            if ipo.get('Issue_Size') and ipo.get('Issue_Size') > 0:
                if ipo.get('QIB_Subscription') is None or ipo.get('QIB_Subscription') <= 0:
                    ipo['QIB_Subscription'] = 1.0
                if ipo.get('HNI_Subscription') is None or ipo.get('HNI_Subscription') <= 0:
                    ipo['HNI_Subscription'] = 1.0
                if ipo.get('Retail_Subscription') is None or ipo.get('Retail_Subscription') <= 0:
                    ipo['Retail_Subscription'] = 1.0
                if ipo.get('PE_Ratio') is None or ipo.get('PE_Ratio') <= 0:
                    ipo['PE_Ratio'] = 20.0
                if ipo.get('OFS_Percentage') is None:
                    ipo['OFS_Percentage'] = 0.5
                if ipo.get('GMP_Listing_Day') is None:
                    ipo['GMP_Listing_Day'] = 0
                if ipo.get('Positive_Listing_Gain') is None:
                    ipo['Positive_Listing_Gain'] = ipo.get('GMP_Listing_Day', 0) > 0
                if not ipo.get('Sector'):
                    ipo['Sector'] = 'General'
                cleaned_data.append(ipo)
        self.ipo_data = cleaned_data

    def save_to_csv(self, filename='indian_ipo_data.csv'):
        if not self.ipo_data:
            print("\nNo IPO data collected. Please check your internet connection and try again.")
            return None
        
        self.clean_and_normalize()
        
        df = pd.DataFrame(self.ipo_data)
        required_columns = [
            'Company_Name', 'Symbol', 'Issue_Size', 'QIB_Subscription',
            'HNI_Subscription', 'Retail_Subscription', 'PE_Ratio',
            'OFS_Percentage', 'GMP_Listing_Day', 'Positive_Listing_Gain', 'Sector'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        df = df[required_columns]
        df.to_csv(filename, index=False)
        
        print(f"\n{'=' * 60}")
        print(f"Successfully saved {len(df)} IPO records to {filename}")
        print(f"{'=' * 60}")
        print(f"\nData Summary:")
        print(df.describe())
        print(f"\nSample records:")
        print(df.head(10).to_string())
        
        return filename

if __name__ == '__main__':
    scraper = EnhancedIndianIPODataScraper()
    scraper.scrape_all_sources()
    scraper.save_to_csv('indian_ipo_data.csv')
