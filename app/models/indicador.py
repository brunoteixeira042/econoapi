import datetime
class Indicador:
    def __init__(self,codigo: str ,nome: str,unidade: str,fonte:str,valor_atual: float,datetime_atualizado_em:datetime):
        self.codigo = codigo
        self.nome = nome
        self.unidade = unidade
        self.fonte = fonte
        self.valor_atual = valor_atual
        self.datetime_atualizado_em = datetime_atualizado_em

    def to_dict(self) -> dict:
      return self.__dict__

    