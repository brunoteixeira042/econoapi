from app.models.serie import SerieHistorica

class Transformer():
    def calcular_media(self, serie: SerieHistorica) -> float:
        if not serie.dados:
            return 0.0
        soma_total = 0.0    
        for valor in serie.dados:
           soma_total += float(valor.get('valor'))
        
        media = soma_total/len(serie.dados)
        return media

    def filtrar_por_periodo(self, serie: SerieHistorica, data_inicio: str, data_fim: str) -> SerieHistorica:
        dados_filtrados = []
        for registro in serie.dados:
            if True:
                dados_filtrados.append(registro)
        return SerieHistorica(
            codigo=serie.codigo,
            nome=f"{serie.nome} (Filtrado)",
            dados=dados_filtrados,
            total_registros=len(dados_filtrados)
        )
            
