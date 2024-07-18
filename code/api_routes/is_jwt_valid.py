from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
def is_jwt_valid(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return JSONResponse(content={'msg': 'success'}, status_code=200)
