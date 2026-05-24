from fastapi import APIRouter, HTTPException
from app.core.collector import DataCollector
from app.core.transformer import Transformer
from app.core.cache import CacheManager
from app.database.bcb import BCBDataSource
from app.database.ibge import IBGEDataSource

router = APIRouter(prefix="/api")

coletor = DataCollector()
coletor.adicionar_fonte(BCBDataSource())
coletor.adicionar_fonte(IBGEDataSource())

transformer = Transformer()
cache = CacheManager()


@router.get("/indicadores")
def rota_listar_indicadores():
    catalogo_completo = []
    for fonte in coletor.fontes:
        catalogo_completo.extend(fonte.listar_indicadores())
    return catalogo_completo


@router.get("/dados/{fonte}/{codigo}")
def rota_buscar_dados(fonte: str, codigo: str):
    try:
        serie = coletor.coletar_por_nome(fonte, codigo)
        return {
            "fonte": fonte,
            "codigo": codigo,
            "nome": serie.nome,
            "dados": serie.dados
        }
        
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/dados/{fonte}/{codigo}/media")
def rota_calcular_media(fonte: str, codigo: str):
    try:
        serie = coletor.coletar_por_nome(fonte, codigo)
        
        # 2. Usa o Transformer para calcular a média dos dados
        media_calculada = transformer.calcular_media(serie)
        
        return {
            "fonte": fonte,
            "codigo": codigo,
            "indicador": serie.nome,
            "media": media_calculada
        }
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))