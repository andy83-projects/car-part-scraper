"""Car-part.com form parser to extract valid search options"""
import httpx
from bs4 import BeautifulSoup
import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def get_search_form_data(year: int, make: str, model: str) -> Optional[Dict]:
    """
    Get the search form and extract hidden fields
    
    This mimics loading the page and getting the sessionID and other hidden values
    """
    base_url = "https://www.car-part.com"
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            # First, get the main page to establish session
            logger.info("Fetching car-part.com homepage to establish session")
            response = await client.get(base_url)
            
            # The form might be on the homepage or a dedicated search page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the search form
            form = soup.find('form', {'action': re.compile(r'search\.cgi')})
            
            if not form:
                logger.error("Could not find search form on page")
                return None
            
            # Extract all hidden input fields
            hidden_fields = {}
            for input_tag in form.find_all('input', type='hidden'):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    hidden_fields[name] = value
            
            logger.info(f"Found {len(hidden_fields)} hidden form fields")
            logger.info(f"Hidden fields: {hidden_fields}")
            
            return hidden_fields
            
        except Exception as e:
            logger.error(f"Error fetching form data: {e}")
            return None
