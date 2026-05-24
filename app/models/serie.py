import pandas as pd
class SerieHistorica:
    def __init__(self,codigo: str, nome: str, dados:list, total_registros: int):
        self.codigo = codigo
        self.nome = nome
        self.dados = dados
        self.total_registros = total_registros
    
    def ultimo_valor(self) -> float:
        if not self.dados:
            return 0
        else:
            ultimo_valor = self.dados[-1]
        return ultimo_valor.get('valor',0.0)
    
    def to_dataframe(self)-> pd.DataFrame:
        if not self.dados:
            return pd.DataFrame()
        else:
            df_dados = pd.DataFrame(self.dados)
        return df_dados

    def to_dict(self)-> dict:
        return self.__dict__