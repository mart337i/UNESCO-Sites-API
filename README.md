# Heritage Sites API Usage Guide

This API provides comprehensive access to UNESCO World Heritage Sites data.

## Base URL

All endpoints are prefixed with `/sites`

## Available Endpoints

### Core Endpoints

1. **Get All Sites** 
   - `GET /sites/all?page=1&per_page=100`
   - Returns all heritage sites with pagination

2. **Filter Sites**
   - `GET /sites/filter?country=France&category=Cultural&year_from=1980&year_to=2010`
   - Supports multiple filter parameters:
     - `country`: Filter by country name
     - `region`: Filter by region
     - `category`: Filter by category (cultural, natural, mixed)
     - `danger`: Filter by danger status (true/false)
     - `transboundary`: Filter by transboundary status (true/false)
     - `year_from`: Filter by inscription year (from)
     - `year_to`: Filter by inscription year (to)
     - `search`: Search in name and description
     - `criteria`: Filter by criteria (comma-separated, e.g. 'c1,n7')
     - `page`: Page number
     - `per_page`: Items per page

3. **Get Site Detail**
   - `GET /sites/detail/{site_id}`
   - Returns detailed information about a specific site

4. **Search Sites**
   - `GET /sites/search?q=pyramid`
   - Searches site names, descriptions, and justifications

### Reference Data Endpoints

5. **Get Countries**
   - `GET /sites/countries`
   - Returns list of all countries with heritage sites

6. **Get Regions**
   - `GET /sites/regions`
   - Returns list of all regions

7. **Get Categories**
   - `GET /sites/categories`
   - Returns list of all site categories

8. **Get Criteria Information**
   - `GET /sites/criteria`
   - Returns information about UNESCO World Heritage criteria

### Advanced Filtering

9. **Sites by Country**
   - `GET /sites/sites-by-country/{country}`
   - Returns all sites for a specific country

10. **Sites by Criteria**
    - `GET /sites/sites-by-criteria/{criterion}`
    - Returns all sites that meet a specific criterion (e.g., c1, n7)

11. **Sites by Year**
    - `GET /sites/sites-by-year/{year}`
    - Returns all sites inscribed in a specific year

12. **Sites in Danger**
    - `GET /sites/sites-in-danger`
    - Returns all sites that are in danger

13. **Transboundary Sites**
    - `GET /sites/sites-transboundary`
    - Returns all transboundary sites

### Analytics and Visualization

14. **Site Statistics**
    - `GET /sites/stats`
    - Returns general statistics about heritage sites

15. **GeoJSON Data**
    - `GET /sites/geo?country=Italy&category=Cultural`
    - Returns GeoJSON-compatible data for map visualization
    - Supports filtering by country, region, category, criteria, danger, and transboundary status

### Database Management

16. **Upload XLS**
    - `POST /sites/upload-xls/`
    - Upload an Excel file to update the database

## Examples

### Example 1: Filter sites in a specific region with criteria

```
GET /sites/filter?region=Europe&criteria=c1,c2&danger=true
```

This will return all sites in Europe that meet criteria C1 and C2 and are in danger.

### Example 2: Get all cultural sites in a specific country

```
GET /sites/filter?country=Egypt&category=Cultural
```

This will return all cultural sites in Egypt.

### Example 3: Search for sites containing a specific term

```
GET /sites/search?q=temple
```

This will return all sites with "temple" in their name or description.

### Example 4: Get GeoJSON data for visualization

```
GET /sites/geo?category=Natural&danger=true
```

This will return GeoJSON data for all natural sites that are in danger, suitable for displaying on a map.

