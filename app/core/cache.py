from app.models.serie import SerieHistorica

class CacheManager:
    def __init__(self):
        # Dicionário privado que vai guardar os dados na memória RAM
        self._dados_salvos: dict = {}

    def salvar(self, chave: str, serie: SerieHistorica) -> None:
        """Guarda uma série histórica no cache associada a uma chave """
        self._dados_salvos[chave] = serie

    def buscar(self, chave: str) -> SerieHistorica | None:
        """Procura uma chave no cache. Se existir, devolve os dados; se não, devolve None."""
        # O método .get() do dicionário devolve None automaticamente se a chave não existir
        return self._dados_salvos.get(chave)