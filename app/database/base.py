from abc import ABC, abstractmethod
from app.models.serie import SerieHistorica

class DataSource(ABC):
    def __init__(self,nome: str, base_url:str):
       self.nome = nome
       self.base_url = base_url

    @abstractmethod
    def fetch(self,codigo: str)-> SerieHistorica:
        """Busca os dados na API externa e retorna um objeto SerieHistorica"""
        pass

    
    @abstractmethod
    def listar_indicadores(self)->list:
        """Retorna uma lista dos indicadores disponíveis nesta fonte"""
        pass

    
