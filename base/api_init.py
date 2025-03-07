# Standard library imports
import os

# Third-party imports
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# Local application imports
from .utils import register_routes

# Miscellaneous
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()


def create_app():
    description = f"API"
    app = FastAPI(
        title="UNESCO World Heritage Sites",
        openapi_url=f"/openapi.json",
        docs_url="/docs/",
        description=description,
    )
    setup_base_routes(app=app)
    setup_addon_routers(app=app)
    use_route_names_as_operation_ids(app=app)

    setup_middleware(app=app)
    return app

def setup_base_routes(app: FastAPI) -> None:
    # Base Routes 
    pass

def setup_addon_routers(app: FastAPI) -> None:
    """
        Import all routes using dynamic importing (Reflections)
    """
    register_routes(app=app)



def setup_middleware(app : FastAPI):
    origins = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:8080",
    ]

    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_credentials=True,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "Range"],
    )

    # app.add_middleware(cs
    #     # Ensures all trafic to server is ssl encrypted or is rederected to https / wss
    #     middleware_class=HTTPSRedirectMiddleware
    # )

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    route_names = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in route_names:
                raise Exception(f"Route function names {[route.name]} should be unique")
            route.operation_id = route.name
            route_names.add(route.name)