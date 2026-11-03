from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.prediction import router as prediction_router


app = FastAPI(
    title="Customer Churn Prediction API",
    description="Backend API for the Customer Churn Prediction System",
    version="1.0.0"
)


# Allow the React frontend (Vite dev server) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(prediction_router)


@app.get("/")
def home():
    return {
        "message": "Customer Churn Prediction API is running"
    }