"""Car-part.com scraper"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchParams:
    """Search parameters for car-part.com"""
    year: int
    make: str
    model: str
    part_type: str = "Cylinder Head"
    zip_code: str = "07001"
    distance: int = 100  # miles


async def search_carpart(params: SearchParams) -> str:
    """
    Search car-part.com and return raw HTML
    
    Args:
        params: Search parameters
        
    Returns:
        Raw HTML response from car-part.com
    """
    from .part_mappings import get_part_info, get_model_db_id
    
    base_url = "https://www.car-part.com/cgi-bin/search.cgi"
    
    # Get part info
    part_info = get_part_info(params.part_type)
    db_model = get_model_db_id(params.make, params.model, params.year)
    
    # Build form data matching car-part.com's EXACT format from network inspection
    form_data = {
        "ref": "",
        "sessionID": "",
        "iKey": "",
        "userModel": f"{params.make} {params.model}",
        "userPart": part_info["userPart"],
        "uID": "",
        "uPass": "",
        "dbPart": part_info["dbPart"],
        "dbSubPart": "",
        "userLocation": "USA",
        "userPreference": "zip",
        "userPage": "1",
        "confirm_yes": "",
        "confirm_no": "",
        "iCN": "",
        "userClaim": "",
        "userClaimer": "",
        "userLang": "",
        "userZip": params.zip_code,
        "userLat": "",
        "userLong": "",
        "userCSA": "",
        "userMCO": "",
        "userAdjuster": "",
        "userItem": "",
        "limitYears": "",
        "userVIN": "",
        "userVINModelID": "",
        "userIMS": "",
        "imsFullSpecification": "",
        "userInterchange": "",  # Leave empty - may work without it
        "userSearch": "int",
        "dbModel": db_model,
        "vinSearch": "",
        "dummyVar": "",
        "userDate": str(params.year),
        "userDate2": str(params.year),
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            logger.info(f"Searching car-part.com for {params.year} {params.make} {params.model} - {part_info['userPart']}")
            logger.info(f"Using dbPart={part_info['dbPart']}, dbModel={db_model}")
            
            response = await client.post(base_url, data=form_data)
            response.raise_for_status()
            
            logger.info(f"Received {len(response.text)} bytes from car-part.com")
            
            # Check for error messages
            if 'INVALID SELECTION' in response.text:
                logger.error(f"Car-part.com returned error: Invalid selection")
                logger.error(f"Response preview: {response.text[:500]}")
            elif 'no parts found' in response.text.lower():
                logger.info("No parts found for this search")
            
            return response.text
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching car-part.com: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching car-part.com: {e}")
            raise


def parse_html_simple(html: str) -> List[Dict]:
    """
    Simple HTML parser for car-part.com results
    
    Args:
        html: Raw HTML from car-part.com
        
    Returns:
        List of parsed parts
    """
    soup = BeautifulSoup(html, 'html.parser')
    parts = []
    
    # First check if there are no results
    page_text = soup.get_text().lower()
    if 'no parts found' in page_text or 'no listings found' in page_text:
        logger.info("No parts found in search results")
        return []
    
    # Find price indicators
    price_elements = soup.find_all(text=lambda text: text and '$' in text)
    logger.info(f"Found {len(price_elements)} elements with $ signs")
    
    # Look for table structures
    tables = soup.find_all('table')
    logger.info(f"Found {len(tables)} tables in HTML")
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
            
            # Get all text from the row
            row_text = row.get_text(' | ', strip=True)
            
            # Skip header rows
            if any(h in row_text.lower() for h in ['price', 'part', 'description', 'location', 'yard']):
                continue
            
            # Must have either a price or phone number to be valid
            has_price = '$' in row_text
            has_phone = any(c in row_text for c in ['(', ')']) and sum(1 for c in row_text if c.isdigit()) >= 10
            
            if not (has_price or has_phone):
                continue
            
            part_data = {
                'raw_data': row_text,
                'description': '',
                'yard_name': '',
            }
            
            # Extract price
            if '$' in row_text:
                try:
                    prices = re.findall(r'\$([\d,]+\.?\d*)', row_text)
                    if prices:
                        price_str = prices[0].replace(',', '')
                        part_data['price'] = float(price_str)
                except Exception as e:
                    logger.debug(f"Could not parse price from: {row_text}")
            
            # Extract phone
            try:
                phones = re.findall(r'\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}', row_text)
                if phones:
                    part_data['phone'] = phones[0]
            except:
                pass
            
            # Extract mileage
            try:
                mileages = re.findall(r'(\d{1,3}(?:,\d{3})*)[\s]*(mi|mile)', row_text.lower())
                if mileages:
                    mileage_str = mileages[0][0].replace(',', '')
                    part_data['mileage'] = int(mileage_str)
            except:
                pass
            
            # Try to identify yard name
            cells_text = [cell.get_text(strip=True) for cell in cells]
            for cell_text in cells_text:
                if len(cell_text) > 10:
                    if not any(x in cell_text for x in ['$', '(', ')']) and not cell_text.isdigit():
                        part_data['yard_name'] = cell_text
                        break
            
            # Add links if present
            links = row.find_all('a', href=True)
            if links:
                part_data['url'] = links[0]['href']
                if not part_data['url'].startswith('http'):
                    part_data['url'] = 'https://www.car-part.com' + part_data['url']
            
            parts.append(part_data)
    
    logger.info(f"Parsed {len(parts)} parts from HTML")
    
    if len(parts) == 0:
        logger.warning(f"No parts parsed. HTML preview: {html[:500]}")
    
    return parts


async def scrape_and_parse(params: SearchParams, use_ai: bool = False) -> List[Dict]:
    """
    Complete scrape and parse workflow
    
    Args:
        params: Search parameters
        use_ai: Whether to use AI for parsing (not implemented yet)
        
    Returns:
        List of parsed parts
    """
    html = await search_carpart(params)
    
    if use_ai:
        logger.warning("AI parsing not yet implemented, falling back to simple parser")
        return parse_html_simple(html)
    else:
        return parse_html_simple(html)
