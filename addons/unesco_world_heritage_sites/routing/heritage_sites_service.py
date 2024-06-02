from fastapi.routing import APIRouter
from fastapi import UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO

from base.logger import logger as _logger
import os

router = APIRouter(
    prefix=f"/sites",
    tags=["Accses and filter sites"],
)

@router.get("/")
def heritage_sites_root():
    return {"OK" : 200}


@router.post("/upload-xls/")
async def upload_xls(file: UploadFile = File(...)):
    try:
        # Ensure the file is of a supported Excel format
        if not file.filename.endswith(('.xls', '.xlsx')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
        
        # Determine the engine to use based on file extension
        if file.filename.endswith('.xlsx'):
            engine = 'openpyxl'
        else:
            engine = 'xlrd'

        # Read the uploaded xls file
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine=engine)
        return {"status": "File uploaded successfully", "columns": df.columns.tolist()}
    except Exception as e:
        return {"error": str(e)}

@router.post("/countries/")
async def get_countries(file: UploadFile = File(...)):
    try:
        # Ensure the file is of a supported Excel format
        if not file.filename.endswith(('.xls', '.xlsx')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
        
        # Determine the engine to use based on file extension
        if file.filename.endswith('.xlsx'):
            engine = 'openpyxl'
        else:
            engine = 'xlrd'

        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine=engine)
        countries = df['states_name_en'].unique().tolist()
        return {"countries": countries}
    except Exception as e:
        return {"error": str(e)}

@router.post("/sites/")
async def get_sites(file: UploadFile = File(...)):
    try:
        # Ensure the file is of a supported Excel format
        if not file.filename.endswith(('.xls', '.xlsx')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
        
        # Determine the engine to use based on file extension
        if file.filename.endswith('.xlsx'):
            engine = 'openpyxl'
        else:
            engine = 'xlrd'

        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine=engine)
        
        # Group sites by country
        grouped_sites = df.groupby('states_name_en')['name_en'].apply(list).reset_index()
        grouped_sites_dict = grouped_sites.to_dict(orient='records')
        
        return {"grouped_sites": grouped_sites_dict}
    except Exception as e:
        return {"error": str(e)}