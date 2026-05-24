from app.database.base import DataSource

class DataCollector():
    def __init__(self):
        self.fontes: list = []

    def adicionar_fonte(self, fonte) -> None:
        self.fontes.append(fonte)
    
    def coletar_tudo(self) -> list:
        resultados = []
        for fonte in self.fontes:
            for ind in fonte.listar_indicadores():
                try:
                    serie = fonte.fetch(ind['codigo'])
                    resultados.append(serie)
                except Exception:
                    continue
        return resultados
       
    def coletar_por_nome(self, nome: str, codigo: str):
        for fonte in self.fontes:
            if fonte.nome == nome:
                return fonte.fetch(codigo)
        raise ValueError(f"A fonte '{nome}' não foi encontrada no coletor.")    