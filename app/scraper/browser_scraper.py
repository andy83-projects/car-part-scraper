"""Car-part.com scraper using Playwright browser automation"""
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchParams:
    """Search parameters for car-part.com"""
    year: int
    make: str
    model: str
    part_type: str = "Engine Cylinder Head"
    zip_code: str = "07001"
    distance: int = 100
    trim: str = None  # Optional trim, will auto-select first if not specified


async def scrape_with_browser(params: SearchParams) -> str:
    """
    Use Playwright to automate browser and search car-part.com
    
    Returns:
        Raw HTML of results page
    """
    async with async_playwright() as p:
        # Launch browser (headless=True for production)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Go to car-part.com
            logger.info("Loading car-part.com")
            await page.goto("https://www.car-part.com", timeout=30000)
            
            # Wait for form to load
            await page.wait_for_selector('select[name="userDate"]')
            
            # Step 1: Fill initial form
            logger.info(f"Selecting: {params.year} {params.make} {params.model} - {params.part_type}")
            
            # Select year
            await page.select_option('select[name="userDate"]', str(params.year))
            
            # Select make/model
            make_model = f"{params.make} {params.model}"
            await page.select_option('select[name="userModel"]', label=make_model)
            
            # Select part type
            await page.select_option('select[name="userPart"]', label=params.part_type)
            
            # Enter zip code
            await page.fill('input[name="userZip"]', params.zip_code)
            
            # Click first Search button
            await page.click('input[name="Search Car Part Inventory"]')
            
            # Wait for trim selection page
            await page.wait_for_selector('input[name="dummyVar"]', timeout=10000)
            
            # Step 2: Select trim
            logger.info("Trim selection page loaded")
            
            if params.trim:
                # Find specific trim radio button by label
                labels = await page.query_selector_all('label')
                for i, label in enumerate(labels):
                    text = await label.inner_text()
                    if params.trim in text:
                        radios = await page.query_selector_all('input[name="dummyVar"]')
                        await radios[i].click()
                        break
            else:
                # Just click first radio button
                first_radio = await page.query_selector('input[name="dummyVar"]')
                await first_radio.click()
                logger.info("Selected first trim option")
            
            # Click second Search button
            await page.click('input[name="Search Car Part Inventory"]')
            
            # Wait for results
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            # Get HTML
            html = await page.content()
            logger.info(f"Got results page, {len(html)} bytes")
            
            await browser.close()
            return html
            
        except Exception as e:
            logger.error(f"Browser automation error: {e}")
            await browser.close()
            raise


def parse_results_html(html: str) -> List[Dict]:
    """
    Parse results HTML using the logic from the GitHub repo
    
    Based on: https://github.com/chung-chris-zz/car_part_scraper
    """
    soup = BeautifulSoup(html, 'html.parser')
    parts = []
    
    try:
        # Results are in the 5th tbody tag
        tbodies = soup.find_all('tbody')
        if len(tbodies) < 5:
            logger.warning(f"Expected 5+ tbody tags, found {len(tbodies)}")
            return []
        
        results_tbody = tbodies[4]
        rows = results_tbody.find_all('tr')
        
        # First and last tr are not individual listings
        rows = rows[1:-1] if len(rows) > 2 else []
        
        logger.info(f"Found {len(rows)} result rows")
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) < 7:
                continue
            
            part_data = {}
            
            # Cell 0: Year, part, make/model
            try:
                text = cells[0].get_text()
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                part_data['year'] = lines[0][:4] if lines else ''
                part_data['part_type'] = lines[0][4:].strip() if len(lines[0]) > 4 else ''
                part_data['make_model'] = lines[1] if len(lines) > 1 else ''
            except:
                pass
            
            # Cell 1: Description and image
            try:
                img = cells[1].find('img')
                part_data['img_url'] = img['src'] if img else ''
                part_data['description'] = cells[1].get_text(strip=True)
            except:
                pass
            
            # Cell 2: Grade
            try:
                part_data['grade'] = cells[2].get_text(strip=True)
            except:
                pass
            
            # Cell 3: Stock number
            try:
                part_data['stock_number'] = cells[3].get_text(strip=True)
            except:
                pass
            
            # Cell 4: Price
            try:
                price_text = cells[4].get_text(strip=True)
                if '$' in price_text:
                    import re
                    prices = re.findall(r'\$([\\d,]+\\.?\\d*)', price_text)
                    if prices:
                        part_data['price'] = float(prices[0].replace(',', ''))
            except:
                pass
            
            # Cell 5: Dealer info
            try:
                links = cells[5].find_all('a')
                if links:
                    part_data['dealer_name'] = links[0].get_text(strip=True)
                    part_data['dealer_url'] = links[0].get('href', '')
                
                text = cells[5].get_text()
                # Extract phone if present
                import re
                phones = re.findall(r'\\(?\\d{3}\\)?[-\\s]?\\d{3}[-\\s]?\\d{4}', text)
                if phones:
                    part_data['phone'] = phones[0]
            except:
                pass
            
            # Cell 6: Distance
            try:
                part_data['distance_miles'] = cells[6].get_text(strip=True)
            except:
                pass
            
            parts.append(part_data)
        
    except Exception as e:
        logger.error(f"Error parsing results: {e}")
    
    return parts


async def scrape_and_parse_browser(params: SearchParams) -> List[Dict]:
    """
    Complete workflow: browser automation + parsing
    """
    html = await scrape_with_browser(params)
    parts = parse_results_html(html)
    logger.info(f"Parsed {len(parts)} parts from results")
    return parts
