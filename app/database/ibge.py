import requests
from app.database.base import DataSource
from app.models.serie import SerieHistorica

class IBGEDataSource(DataSource):
    def __init__(self):
        super().__init__(
        nome='IBGE', 
        base_url='https://servicodados.ibge.gov.br/api/v3/agregados/{codigo}/periodos/-10/variaveis?localidades=BR'
        )
    
    def fetch(self, codigo) -> SerieHistorica:
        url_final = self.base_url.format(codigo=codigo)
        try:
            response = requests.get(url_final, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
        except Exception as e:
            raise ValueError(f"Erro ao buscar dados do IBGE: {e}")

        dados_formatados = []
        nome_serie = 'Série IPCA' if codigo == '1737' else f'Série IBGE {codigo}'

        if isinstance(dados_api, list) and len(dados_api) > 0:
            # Look for monthly variation (id '63') or fall back to first variable
            variavel = None
            for v in dados_api:
                if v.get("id") == "63":
                    variavel = v
                    break
            if not variavel:
                variavel = dados_api[0]
                
            if variavel:
                nome_serie = variavel.get("variavel", nome_serie)
                resultados = variavel.get("resultados", [])
                if resultados:
                    series = resultados[0].get("series", [])
                    if series:
                        serie_dados = series[0].get("serie", {})
                        for periodo, valor in serie_dados.items():
                            try:
                                data_str = f"{periodo[:4]}-{periodo[4:]}" if len(periodo) == 6 else periodo
                                val_str = valor.replace(",", ".") if valor else "0"
                                dados_formatados.append({
                                    "data": data_str,
                                    "valor": float(val_str)
                                })
                            except (ValueError, TypeError):
                                continue

        return SerieHistorica(codigo=codigo,nome=nome_serie,dados=dados_formatados,total_registros=len(dados_formatados))
    
    
    def listar_indicadores(self)->list:
        return [
            {"codigo": "1737", "nome": "IPCA - Inflação"}
        ]
    
