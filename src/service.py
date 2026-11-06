from datetime import datetime, timedelta, timezone
from typing import cast

import bentoml
import jwt
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from sklearn.linear_model import LinearRegression
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Do not hardcode secrets in production
JWT_SECRET_KEY = (
    '2914d5d479572c037672403f6a02c105bddd92457dc851adbfd8f94eb3648cac'
)
JWT_ALGORITHM = 'HS256'

USERS = {
    'user123': 'password123',
    'user456': 'password456',
}


class Credentials(BaseModel):
    username: str
    password: str


class InputModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gre_score: int
    toefl_score: int
    university_rating: int
    sop: float
    lor: float
    cgpa: float
    research: bool


def create_jwt_token(user_id: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {'sub': user_id, 'exp': expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.endswith('/predict'):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={'detail': 'Missing authentication token'},
                )
            # Expected format: 'Bearer <token>'
            scheme, _, token = auth_header.partition(' ')
            token = token.strip()
            if scheme.lower() != 'bearer' or not token:
                return JSONResponse(
                    status_code=401,
                    content={
                        'detail': 'Malformed authorization header, '
                        'expected: Bearer <token>'
                    },
                )
            try:
                payload = jwt.decode(
                    token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
                )
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=401, content={'detail': 'Token has expired'}
                )
            except jwt.InvalidTokenError:
                return JSONResponse(
                    status_code=401, content={'detail': 'Invalid token'}
                )
            request.state.user = payload.get('sub')
        return await call_next(request)


@bentoml.service
class LRModelService:
    def __init__(self):
        self.model = cast(
            LinearRegression, bentoml.sklearn.load_model('admission_lr:latest')
        )
        self.feature_names = list(self.model.feature_names_in_)

    @bentoml.api
    def predict_array(self, features: list[float]) -> list[float]:
        x = pd.DataFrame([features], columns=self.feature_names)
        pred = self.model.predict(x)
        return pred.tolist()


@bentoml.service
class AdmissionService:
    model_service = bentoml.depends(LRModelService)

    @bentoml.api(route='/login')
    def login(self, credentials: Credentials):
        if USERS.get(credentials.username) == credentials.password:
            token = create_jwt_token(credentials.username)
            return {'token': token}
        return JSONResponse(
            status_code=401, content={'detail': 'Invalid credentials'}
        )

    @bentoml.api(route='/predict')
    def predict(self, input_data: InputModel):
        features = [
            input_data.gre_score,
            input_data.toefl_score,
            input_data.university_rating,
            input_data.sop,
            input_data.lor,
            input_data.cgpa,
            input_data.research,
        ]
        pred = self.model_service.predict_array(features)
        return {'prediction': pred}


# Apply middleware to the whole service: This is the point where the
# JWTAuthMiddleware "intercepts" the /predict endpoint.
AdmissionService.add_asgi_middleware(JWTAuthMiddleware)
