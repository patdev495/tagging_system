from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

async def custom_http_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        status_code = exc.status_code
        detail = exc.detail
    else:
        status_code = 500
        detail = str(exc)
        
    return JSONResponse(
        status_code=status_code,
        content={"error": detail},
    )
