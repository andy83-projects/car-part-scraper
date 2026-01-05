"""Car-part.com part type mappings"""
from typing import Dict

# Part types mapping: name -> (dbPart, description)
PART_TYPES: Dict[str, Dict[str, str]] = {
    "cylinder_head": {
        "name": "Engine Cylinder Head",
        "dbPart": "306.1",
        "userPart": "Engine Cylinder Head"
    },
    "engine": {
        "name": "Engine",
        "dbPart": "300.1",
        "userPart": "Engine"
    },
    "transmission": {
        "name": "Transmission",
        "dbPart": "400.1",
        "userPart": "Transmission"
    },
    "head": {
        "name": "Engine Cylinder Head",
        "dbPart": "306.1",
        "userPart": "Engine Cylinder Head"
    }
}

# Model mappings - we'll need to build these dynamically or scrape them
# For now, hardcode common ones
MODEL_DB_IDS = {
    ("Mitsubishi", "Eclipse", 1992): "51.5.1.1",
    ("Mitsubishi", "Eclipse", 1997): "51.5.1.1",  # Likely same
    ("Mitsubishi", "Lancer", 2003): "51.8.1.1",  # Guess
    ("Hyundai", "Tiburon", 2003): "32.12.1.1",   # Guess
    ("Hyundai", "Elantra", 2004): "32.7.1.1",
    ("Hyundai", "Sonata", 2004): "32.7.1.1",
    ("Kia", "Spectra5", 2007): "34.1.1.1",       # Guess
}


def get_part_info(part_type: str) -> Dict[str, str]:
    """Get part information by type"""
    return PART_TYPES.get(part_type.lower().replace(" ", "_"), PART_TYPES["cylinder_head"])


def get_model_db_id(make: str, model: str, year: int) -> str:
    """Get dbModel ID for make/model/year"""
    key = (make, model, year)
    # Try exact match
    if key in MODEL_DB_IDS:
        return MODEL_DB_IDS[key]
    
    # Try without year (approximate)
    for (m, mo, y), db_id in MODEL_DB_IDS.items():
        if m == make and mo == model:
            return db_id
    
    # Default fallback
    return "1.1.1.1"
