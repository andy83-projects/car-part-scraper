"""Main FastAPI application"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from .config import settings
from .database import get_db, init_db
from .models import Part, SearchRun
from . import vehicles as vehicle_configs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="4G63 Head Finder",
    description="Find compatible cylinder heads for 4G63, G4JS, and Hyundai 2.0L DOHC engines",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="app/templates")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Main dashboard"""
    # Get stats
    total_parts = db.query(Part).count()
    available_parts = db.query(Part).filter(Part.is_available == True).count()
    
    # Get recent parts
    recent_parts = db.query(Part).filter(Part.is_available == True)\
        .order_by(Part.first_seen_at.desc()).limit(20).all()
    
    # Get last search run
    last_run = db.query(SearchRun).order_by(SearchRun.started_at.desc()).first()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_parts": total_parts,
        "available_parts": available_parts,
        "recent_parts": recent_parts,
        "last_run": last_run,
        "app_name": settings.app_name
    })


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": db_status}
        )
    
    return {"status": "healthy", "database": db_status}


@app.get("/api/parts")
async def list_parts(
    skip: int = 0,
    limit: int = 100,
    available_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all parts"""
    query = db.query(Part)
    
    if available_only:
        query = query.filter(Part.is_available == True)
    
    parts = query.order_by(Part.first_seen_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "parts": [
            {
                "id": p.id,
                "description": p.part_description,
                "price": float(p.price) if p.price else None,
                "yard": p.yard_name,
                "location": p.location,
                "mileage": p.mileage,
                "first_seen": p.first_seen_at.isoformat() if p.first_seen_at else None,
                "url": p.url
            }
            for p in parts
        ]
    }


@app.get("/api/parts/{part_id}")
async def get_part(part_id: int, db: Session = Depends(get_db)):
    """Get part details"""
    part = db.query(Part).filter(Part.id == part_id).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    return {
        "id": part.id,
        "description": part.part_description,
        "stock_number": part.stock_number,
        "price": float(part.price) if part.price else None,
        "grade": part.grade,
        "yard": part.yard_name,
        "location": part.location,
        "phone": part.phone,
        "distance": float(part.distance_miles) if part.distance_miles else None,
        "mileage": part.mileage,
        "warranty": part.warranty,
        "notes": part.notes,
        "url": part.url,
        "first_seen": part.first_seen_at.isoformat() if part.first_seen_at else None,
        "last_seen": part.last_seen_at.isoformat() if part.last_seen_at else None,
        "available": part.is_available
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics"""
    total = db.query(Part).count()
    available = db.query(Part).filter(Part.is_available == True).count()
    
    # Average price
    from sqlalchemy import func
    avg_price = db.query(func.avg(Part.price)).filter(
        Part.is_available == True,
        Part.price != None
    ).scalar()
    
    # Price range
    min_price = db.query(func.min(Part.price)).filter(
        Part.is_available == True,
        Part.price != None
    ).scalar()
    
    max_price = db.query(func.max(Part.price)).filter(
        Part.is_available == True,
        Part.price != None
    ).scalar()
    
    # Recent searches
    recent_searches = db.query(SearchRun).order_by(SearchRun.started_at.desc()).limit(10).all()
    
    return {
        "total_parts": total,
        "available_parts": available,
        "unavailable_parts": total - available,
        "average_price": float(avg_price) if avg_price else None,
        "min_price": float(min_price) if min_price else None,
        "max_price": float(max_price) if max_price else None,
        "recent_searches": [
            {
                "id": s.id,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "status": s.status,
                "parts_found": s.total_parts_found,
                "new_parts": s.new_parts_added
            }
            for s in recent_searches
        ]
    }


@app.get("/api/config/vehicles")
async def get_vehicle_configs():
    """Get all vehicle configurations"""
    groups = vehicle_configs.get_all_groups()
    
    return {
        "groups": {
            name: [
                {
                    "name": v.name,
                    "year": v.year,
                    "make": v.make,
                    "model": v.model,
                    "engine": v.engine
                }
                for v in vehicles
            ]
            for name, vehicles in groups.items()
        }
    }


# Placeholder search endpoints (will implement scraping logic next)
@app.get("/api/search/4g63")
async def search_4g63():
    """Search for 4G63 heads"""
    from .scraper.carpart import scrape_and_parse, SearchParams
    from . import vehicles as vehicle_configs
    
    results = []
    for vehicle in vehicle_configs.VEHICLE_4G63:
        try:
            params = SearchParams(
                year=vehicle.year,
                make=vehicle.make,
                model=vehicle.model,
                part_type=vehicle.part_type,
                zip_code="07001",
                distance=100
            )
            parts = await scrape_and_parse(params, use_ai=False)
            results.extend(parts)
        except Exception as e:
            logger.error(f"Error searching {vehicle.name}: {e}")
    
    return {
        "message": f"Found {len(results)} results",
        "vehicles_searched": [v.name for v in vehicle_configs.VEHICLE_4G63],
        "results": results
    }


@app.get("/api/search/g4js")
async def search_g4js():
    """Search for G4JS heads"""
    from .scraper.carpart import scrape_and_parse, SearchParams
    from . import vehicles as vehicle_configs
    
    results = []
    for vehicle in vehicle_configs.VEHICLE_G4JS:
        try:
            params = SearchParams(
                year=vehicle.year,
                make=vehicle.make,
                model=vehicle.model,
                part_type=vehicle.part_type,
                zip_code="07001",
                distance=100
            )
            parts = await scrape_and_parse(params, use_ai=False)
            results.extend(parts)
        except Exception as e:
            logger.error(f"Error searching {vehicle.name}: {e}")
    
    return {
        "message": f"Found {len(results)} results",
        "vehicles_searched": [v.name for v in vehicle_configs.VEHICLE_G4JS],
        "results": results
    }


@app.get("/api/search/hyundai2l")
async def search_hyundai_2l():
    """Search for Hyundai 2.0L heads"""
    from .scraper.carpart import scrape_and_parse, SearchParams
    from . import vehicles as vehicle_configs
    
    results = []
    for vehicle in vehicle_configs.VEHICLE_HYUNDAI_2L:
        try:
            params = SearchParams(
                year=vehicle.year,
                make=vehicle.make,
                model=vehicle.model,
                part_type=vehicle.part_type,
                zip_code="07001",
                distance=100
            )
            parts = await scrape_and_parse(params, use_ai=False)
            results.extend(parts)
        except Exception as e:
            logger.error(f"Error searching {vehicle.name}: {e}")
    
    return {
        "message": f"Found {len(results)} results",
        "vehicles_searched": [v.name for v in vehicle_configs.VEHICLE_HYUNDAI_2L],
        "results": results
    }


@app.get("/api/debug/search")
async def debug_search(year: int, make: str, model: str, part: str = "Cylinder Head"):
    """Debug endpoint to see raw HTML from car-part.com"""
    from .scraper.carpart import search_carpart, SearchParams, parse_html_simple
    
    try:
        params = SearchParams(
            year=year,
            make=make,
            model=model,
            part_type=part,  # Allow custom part type
            zip_code="07001",
            distance=100
        )
        
        # Get raw HTML
        html = await search_carpart(params)
        
        # Try to parse
        parts = parse_html_simple(html)
        
        # Check for "no results" indicators
        no_results_found = any(phrase in html.lower() for phrase in [
            'no parts found',
            'no listings found',
            'no results',
            'try broadening your search'
        ])
        
        return {
            "html_length": len(html),
            "html_preview": html[:2000],  # More preview
            "html_full": html,  # Full HTML for debugging
            "parts_found": len(parts),
            "parts": parts[:5],
            "no_results_indicators": no_results_found
        }
    except Exception as e:
        logger.error(f"Debug search error: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }
