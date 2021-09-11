#  Copyright (c) 2020 - 2021 Persanix LLC. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import FileResponse, Response

from endrpi.model.message import MessageData
from endrpi.routes.pin import router as pin_router
from endrpi.routes.system import router as system_router
from endrpi.routes.websocket import router as websocket_router

app = FastAPI(
    title='Endrpi REST API',
    description='Interactive documentation for the Endrpi REST API.',
    version='0.1.0',
    docs_url=None,
    redoc_url=None
)

app.include_router(websocket_router)
app.include_router(system_router, tags=['system'])
app.include_router(pin_router, tags=['pins'])

public_path = os.path.join(Path(__file__).parent, "_public")
app.mount('/public', StaticFiles(directory=public_path, html=True, check_dir=True), name='public')


@app.get("/docs", include_in_schema=False)
async def get_docs():
    public_path = 'public/swagger-ui'
    swagger_js_path = f'{public_path}/swagger-ui-bundle.js'
    swagger_css_path = f'{public_path}/swagger-ui.css'

    if os.path.exists(swagger_js_path) and os.path.exists(swagger_css_path):
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + ' - Swagger UI',
            swagger_js_url=swagger_js_path,
            swagger_css_url=swagger_css_path,
        )
    else:
        return Response(
            f'Swagger-UI files not found in "{public_path}". '
            f'More details are available on the installation page of the project documentation website.',
            status_code=404
        )


@app.get("/", include_in_schema=False)
async def get_docs():
    return FileResponse(os.path.join(public_path, 'index.html'))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = str(exc).replace('\n', '')
    message = MessageData(message=errors)
    json_content = jsonable_encoder(message)
    return JSONResponse(status_code=400, content=json_content)
