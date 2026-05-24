import requests
from datetime import datetime, timedelta
from app.models.serie import SerieHistorica
from app.database.base import DataSource

class BCBDataSource(DataSource):
    def __init__(self):
      super().__init__(
          nome = 'Banco do Brasil',
          base_url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json'
        )

    def fetch(self, codigo)-> SerieHistorica:
        # Calculate dataInicial (last 365 days)
        data_inicial = (datetime.now() - timedelta(days=365)).strftime('%d/%m/%Y')
        url_final = f"{self.base_url.format(codigo=codigo)}&dataInicial={data_inicial}"
        
        try:
            response = requests.get(url_final, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
        except Exception as e:
            raise ValueError(f"Erro ao buscar dados do Banco Central: {e}")

        dados_formatados = []
        if isinstance(dados_api, list):
            for item in dados_api:
                try:
                    dados_formatados.append({
                        "data": item["data"],
                        "valor": float(item["valor"].replace(",", "."))
                    })
                except (ValueError, KeyError, TypeError):
                    continue

        nome_serie = 'Série Selic' if codigo == '11' else f'Série SGS {codigo}'
        return SerieHistorica(codigo=codigo,nome=nome_serie,dados=dados_formatados,total_registros=len(dados_formatados))
    
    
    def listar_indicadores(self) -> list:
        return [
            {"codigo": "11", "nome": "Taxa SELIC"}
        ]