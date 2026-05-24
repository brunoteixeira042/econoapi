from fastapi import FastAPI
from app.routers.router import router

app = FastAPI(
    title="EconoAPI",
    description="API para coleta e análise de dados macroeconômicos em tempo real.",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao EconoAPI! Acesse /docs para visualizar a documentação."}
