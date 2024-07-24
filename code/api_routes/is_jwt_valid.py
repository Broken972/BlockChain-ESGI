from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
async def is_jwt_valid(Authorize):
    Authorize.jwt_required()
    return "msg: ok"