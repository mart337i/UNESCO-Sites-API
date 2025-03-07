from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import pandas as pd
from io import BytesIO
import os
import sqlite3

# Create SQLAlchemy engine
DATABASE_URL = f"sqlite:///sites_xlsx_export.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models for response
class Site(BaseModel):
    unique_number: Optional[int] = None
    id_no: Optional[int] = None
    rev_bis: Optional[str] = None
    name_en: str
    name_fr: Optional[str] = None
    short_description_en: Optional[str] = None
    short_description_fr: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    category: Optional[str] = None
    category_short: Optional[str] = None
    states_name_en: str
    region_en: Optional[str] = None
    date_inscribed: Optional[int] = None

class SiteDetail(Site):
    justification_en: Optional[str] = None
    justification_fr: Optional[str] = None
    secondary_dates: Optional[str] = None
    danger: Optional[int] = None
    date_end: Optional[float] = None
    danger_list: Optional[str] = None
    area_hectares: Optional[float] = None
    c1: Optional[int] = None
    c2: Optional[int] = None
    c3: Optional[int] = None
    c4: Optional[int] = None
    c5: Optional[int] = None
    c6: Optional[int] = None
    n7: Optional[int] = None
    n8: Optional[int] = None
    n9: Optional[int] = None
    n10: Optional[int] = None
    criteria_txt: Optional[str] = None
    states_name_fr: Optional[str] = None
    region_fr: Optional[str] = None
    iso_code: Optional[str] = None
    udnp_code: Optional[str] = None
    transboundary: Optional[int] = None

# Helper to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/sites",
    tags=["Heritage Sites API"],
)

# Add additional models for advanced features
class Pagination(BaseModel):
    total: int
    page: int
    total_pages: int
    per_page: int
    
class PaginatedResponse(BaseModel):
    data: List[Dict[str, Any]] 
    pagination: Pagination

@router.get("/")
def heritage_sites_root():
    """
    Root endpoint for Heritage Sites API with documentation links
    """
    return {
        "message": "Heritage Sites API",
        "version": "1.0.0",
        "endpoints": {
            "all_sites": "/sites/all",
            "filter_sites": "/sites/filter",
            "site_detail": "/sites/detail/{site_id}",
            "countries": "/sites/countries",
            "regions": "/sites/regions",
            "categories": "/sites/categories",
            "sites_by_country": "/sites/sites-by-country/{country}",
            "sites_by_criteria": "/sites/sites-by-criteria/{criterion}",
            "sites_by_year": "/sites/sites-by-year/{year}",
            "sites_in_danger": "/sites/sites-in-danger",
            "transboundary_sites": "/sites/sites-transboundary",
            "criteria_info": "/sites/criteria",
            "statistics": "/sites/stats",
            "search": "/sites/search?q={search_term}",
            "geo_data": "/sites/geo"
        },
        "documentation": "/docs"
    }

@router.get("/all", response_model=List[Site])
def get_all_sites(
    page: int = Query(1, description="Page number (starts from 1)"),
    per_page: int = Query(100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all heritage sites with pagination
    """
    # Calculate pagination values
    skip = (page - 1) * per_page
    
    query = text("""
        SELECT unique_number, id_no, rev_bis, name_en, name_fr, short_description_en, 
               short_description_fr, longitude, latitude, category, category_short, 
               states_name_en, region_en, date_inscribed 
        FROM sites_xlsx_export
        LIMIT :limit OFFSET :skip
    """)
    
    result = db.execute(query, {"skip": skip, "limit": per_page})
    sites = []
    for row in result:
        # Convert row to dictionary properly
        site = {}
        for column, value in row._mapping.items():
            site[column] = value
        sites.append(site)
    
    return sites

@router.get("/filter", response_model=List[Site])
def filter_sites(
    country: Optional[str] = Query(None, description="Filter by country name"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category (cultural, natural, mixed)"),
    danger: Optional[bool] = Query(None, description="Filter by danger status"),
    year_from: Optional[int] = Query(None, description="Filter by inscription year (from)"),
    year_to: Optional[int] = Query(None, description="Filter by inscription year (to)"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    criteria: Optional[str] = Query(None, description="Filter by criteria (comma-separated, e.g. 'c1,n7')"),
    transboundary: Optional[bool] = Query(None, description="Filter by transboundary status"),
    page: int = Query(1, description="Page number (starts from 1)"),
    per_page: int = Query(100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Filter heritage sites by various parameters
    """
    # Start building the query
    query_parts = [
        """
        SELECT unique_number, id_no, rev_bis, name_en, name_fr, short_description_en, 
               short_description_fr, longitude, latitude, category, category_short, 
               states_name_en, region_en, date_inscribed 
        FROM sites_xlsx_export 
        WHERE 1=1
        """
    ]
    params = {}
    
    # Add filters
    if country:
        query_parts.append("AND states_name_en LIKE :country")
        params["country"] = f"%{country}%"
    
    if region:
        query_parts.append("AND region_en LIKE :region")
        params["region"] = f"%{region}%"
    
    if category:
        query_parts.append("AND category_short LIKE :category")
        params["category"] = f"%{category}%"
    
    if danger is not None:
        query_parts.append("AND danger = :danger")
        params["danger"] = 1 if danger else 0
    
    if transboundary is not None:
        query_parts.append("AND transboundary = :transboundary")
        params["transboundary"] = 1 if transboundary else 0
    
    if year_from:
        query_parts.append("AND date_inscribed >= :year_from")
        params["year_from"] = year_from
    
    if year_to:
        query_parts.append("AND date_inscribed <= :year_to")
        params["year_to"] = year_to
    
    if search:
        query_parts.append("AND (name_en LIKE :search OR name_fr LIKE :search OR short_description_en LIKE :search OR short_description_fr LIKE :search)")
        params["search"] = f"%{search}%"
    
    if criteria:
        criteria_list = criteria.split(',')
        for i, criterion in enumerate(criteria_list):
            criterion = criterion.strip().lower()
            if criterion.startswith('c') and criterion[1:].isdigit():
                col_num = int(criterion[1:])
                if 1 <= col_num <= 6:
                    query_parts.append(f"AND c{col_num} = 1")
            elif criterion.startswith('n') and criterion[1:].isdigit():
                col_num = int(criterion[1:])
                if 7 <= col_num <= 10:
                    query_parts.append(f"AND n{col_num} = 1")
    
    # Calculate pagination values
    skip = (page - 1) * per_page
    
    # Add pagination
    query_parts.append("LIMIT :limit OFFSET :skip")
    params["skip"] = skip
    params["limit"] = per_page
    
    # Execute query
    full_query = " ".join(query_parts)
    result = db.execute(text(full_query), params)
    sites = [dict(row) for row in result]
    
    return sites

@router.get("/detail/{site_id}", response_model=SiteDetail)
def get_site_detail(
    site_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific heritage site
    """
    query = text("""
        SELECT * FROM sites_xlsx_export WHERE id_no = :site_id
    """)
    
    result = db.execute(query, {"site_id": site_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Site with ID {site_id} not found")
    
    # Convert row to dict
    site_data = dict(result)
    return site_data

@router.get("/countries", response_model=List[str])
def get_countries(db: Session = Depends(get_db)):
    """
    Get a list of all countries with heritage sites
    """
    query = text("""
        SELECT DISTINCT states_name_en FROM sites_xlsx_export 
        WHERE states_name_en IS NOT NULL
        ORDER BY states_name_en
    """)
    
    result = db.execute(query)
    countries = [row[0] for row in result if row[0]]
    
    return countries

@router.get("/regions", response_model=List[str])
def get_regions(db: Session = Depends(get_db)):
    """
    Get a list of all regions with heritage sites
    """
    query = text("""
        SELECT DISTINCT region_en FROM sites_xlsx_export 
        WHERE region_en IS NOT NULL
        ORDER BY region_en
    """)
    
    result = db.execute(query)
    regions = [row[0] for row in result if row[0]]
    
    return regions

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """
    Get a list of all site categories
    """
    query = text("""
        SELECT DISTINCT category_short FROM sites_xlsx_export 
        WHERE category_short IS NOT NULL
        ORDER BY category_short
    """)
    
    result = db.execute(query)
    categories = [row[0] for row in result if row[0]]
    
    return categories

@router.get("/sites-by-country/{country}", response_model=List[Site])
def get_sites_by_country(
    country: str,
    db: Session = Depends(get_db)
):
    """
    Get all heritage sites for a specific country
    """
    query = text("""
        SELECT unique_number, id_no, rev_bis, name_en, name_fr, short_description_en, 
               short_description_fr, longitude, latitude, category, category_short, 
               states_name_en, region_en, date_inscribed 
        FROM sites_xlsx_export 
        WHERE states_name_en = :country
        ORDER BY name_en
    """)
    
    result = db.execute(query, {"country": country})
    sites = [dict(row) for row in result]
    
    return sites

@router.get("/criteria")
def get_criteria_info():
    """
    Get information about the UNESCO World Heritage criteria
    """
    criteria_info = {
        "cultural": [
            {"id": "c1", "description": "Represents a masterpiece of human creative genius"},
            {"id": "c2", "description": "Exhibits an important interchange of human values"},
            {"id": "c3", "description": "Bears a unique or exceptional testimony to a cultural tradition"},
            {"id": "c4", "description": "Outstanding example of a type of building, architecture or landscape"},
            {"id": "c5", "description": "Outstanding example of a traditional human settlement or land-use"},
            {"id": "c6", "description": "Associated with events or living traditions, ideas, or beliefs"}
        ],
        "natural": [
            {"id": "n7", "description": "Contains superlative natural phenomena or exceptional natural beauty"},
            {"id": "n8", "description": "Outstanding example representing major stages of Earth's history"},
            {"id": "n9", "description": "Outstanding example representing significant ecological and biological processes"},
            {"id": "n10", "description": "Contains the most important natural habitats for conservation of biological diversity"}
        ]
    }
    return criteria_info

@router.get("/stats")
def get_site_statistics(db: Session = Depends(get_db)):
    """
    Get general statistics about the heritage sites
    """
    stats = {}
    
    # Total count
    query = text("SELECT COUNT(*) FROM sites_xlsx_export")
    stats["total_sites"] = db.execute(query).scalar()
    
    # Count by category
    query = text("""
        SELECT category_short, COUNT(*) 
        FROM sites_xlsx_export 
        WHERE category_short IS NOT NULL
        GROUP BY category_short
    """)
    result = db.execute(query)
    stats["sites_by_category"] = {row[0]: row[1] for row in result if row[0]}
    
    # Count by region
    query = text("""
        SELECT region_en, COUNT(*) 
        FROM sites_xlsx_export 
        WHERE region_en IS NOT NULL
        GROUP BY region_en
        ORDER BY COUNT(*) DESC
    """)
    result = db.execute(query)
    stats["sites_by_region"] = {row[0]: row[1] for row in result if row[0]}
    
    # Count in danger
    query = text("SELECT COUNT(*) FROM sites_xlsx_export WHERE danger = 1")
    stats["sites_in_danger"] = db.execute(query).scalar()
    
    # Count transboundary sites
    query = text("SELECT COUNT(*) FROM sites_xlsx_export WHERE transboundary = 1")
    stats["transboundary_sites"] = db.execute(query).scalar()
    
    # Count by criteria (cultural and natural)
    stats["criteria_counts"] = {}
    for i in range(1, 7):
        query = text(f"SELECT COUNT(*) FROM sites_xlsx_export WHERE c{i} = 1")
        stats["criteria_counts"][f"c{i}"] = db.execute(query).scalar()
    
    for i in range(7, 11):
        query = text(f"SELECT COUNT(*) FROM sites_xlsx_export WHERE n{i} = 1")
        stats["criteria_counts"][f"n{i}"] = db.execute(query).scalar()
    
    # Count by decade
    query = text("""
        SELECT 
            ((date_inscribed/10)*10) AS decade,
            COUNT(*) 
        FROM sites_xlsx_export 
        WHERE date_inscribed IS NOT NULL
        GROUP BY decade
        ORDER BY decade
    """)
    result = db.execute(query)
    stats["sites_by_decade"] = {f"{row[0]}s": row[1] for row in result if row[0] is not None}
    
    return stats

@router.get("/search", response_model=List[Site])
def search_sites(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Search for heritage sites by name or description
    """
    query = text("""
        SELECT unique_number, id_no, rev_bis, name_en, name_fr, short_description_en, 
               short_description_fr, longitude, latitude, category, category_short, 
               states_name_en, region_en, date_inscribed 
        FROM sites_xlsx_export 
        WHERE name_en LIKE :search
           OR name_fr LIKE :search
           OR short_description_en LIKE :search
           OR short_description_fr LIKE :search
           OR justification_en LIKE :search
           OR justification_fr LIKE :search
           OR states_name_en LIKE :search
           OR region_en LIKE :search
        LIMIT 100
    """)
    
    result = db.execute(query, {"search": f"%{q}%"})
    sites = [dict(row) for row in result]
    
    return sites

@router.get("/geo", response_model=List[Dict[str, Any]])
def get_geojson_data(
    country: Optional[str] = Query(None, description="Filter by country name"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    criteria: Optional[str] = Query(None, description="Filter by criteria (e.g., 'c1')"),
    danger: Optional[bool] = Query(None, description="Filter by danger status"),
    transboundary: Optional[bool] = Query(None, description="Filter by transboundary status"),
    db: Session = Depends(get_db)
):
    """
    Get GeoJSON-compatible data for map visualization
    """
    query_parts = [
        """
        SELECT id_no, name_en, longitude, latitude, category_short, 
               states_name_en, region_en, danger, transboundary,
               c1, c2, c3, c4, c5, c6, n7, n8, n9, n10
        FROM sites_xlsx_export 
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        """
    ]
    params = {}
    
    if country:
        query_parts.append("AND states_name_en = :country")
        params["country"] = country
    
    if region:
        query_parts.append("AND region_en = :region")
        params["region"] = region
    
    if category:
        query_parts.append("AND category_short = :category")
        params["category"] = category
    
    if danger is not None:
        query_parts.append("AND danger = :danger")
        params["danger"] = 1 if danger else 0
    
    if transboundary is not None:
        query_parts.append("AND transboundary = :transboundary")
        params["transboundary"] = 1 if transboundary else 0
    
    if criteria:
        criteria_type = criteria[0].lower()
        criteria_num = criteria[1:]
        if criteria_type == 'c' and criteria_num.isdigit() and 1 <= int(criteria_num) <= 6:
            query_parts.append(f"AND c{criteria_num} = 1")
        elif criteria_type == 'n' and criteria_num.isdigit() and 7 <= int(criteria_num) <= 10:
            query_parts.append(f"AND n{criteria_num} = 1")
    
    query = text(" ".join(query_parts))
    result = db.execute(query, params)
    
    features = []
    for row in result:
        site = dict(row)
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [site["longitude"], site["latitude"]]
            },
            "properties": {
                "id": site["id_no"],
                "name": site["name_en"],
                "category": site["category_short"],
                "country": site["states_name_en"],
                "region": site["region_en"],
                "danger": bool(site["danger"]),
                "transboundary": bool(site["transboundary"]),
                "criteria": {
                    "c1": bool(site["c1"]),
                    "c2": bool(site["c2"]),
                    "c3": bool(site["c3"]),
                    "c4": bool(site["c4"]),
                    "c5": bool(site["c5"]),
                    "c6": bool(site["c6"]),
                    "n7": bool(site["n7"]),
                    "n8": bool(site["n8"]),
                    "n9": bool(site["n9"]),
                    "n10": bool(site["n10"])
                }
            }
        }
    
    return features
