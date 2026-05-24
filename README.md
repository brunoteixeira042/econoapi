# 📈 EconoAPI - API e Dashboard de Indicadores Econômicos

O **EconoAPI** é uma plataforma completa escrita em Python para coleta, análise e visualização de indicadores macroeconômicos brasileiros em tempo real. O sistema consome dados diretamente das APIs oficiais do **Banco Central do Brasil (BCB)** e do **Instituto Brasileiro de Geografia e Estatística (IBGE)**, fornecendo tanto uma API RESTful de alta performance (FastAPI) quanto um Dashboard web interativo (Streamlit).

---

## 🚀 Recursos Principais

* **Conexão em Tempo Real**: Integração robusta via HTTP com as APIs públicas oficiais do BCB (SGS) e IBGE (Agregados de inflação).
* **API RESTful (FastAPI)**: Endpoints rápidos e estruturados para listar indicadores, buscar séries históricas e calcular médias estatísticas em tempo real.
* **Dashboard Interativo (Streamlit)**:
  * **Visualização Flexível**: Escolha entre foco total na SELIC, foco total no IPCA ou comparação simétrica entre ambos.
  * **Gráficos Responsivos**: Visualização em barras e linhas com controles interativos de zoom e exportação.
  * **Atualização Imediata**: Botão integrado para limpar o cache local e buscar dados novos diretamente da web instantaneamente.
  * **Exportador de Dados**: Download de dados históricos em formato CSV.
  * **Suporte a Dark Mode**: Cores e contrastes otimizados para se ajustar ao tema claro ou escuro do navegador.
* **Processamento Estatístico**: Lógica isolada (`Transformer`) para calcular médias e manipular séries temporais.

---

## 📂 Estrutura do Projeto

A organização dos arquivos segue as melhores práticas de modularidade em Python:

```text
econoapi/
├── app/
│   ├── core/
│   │   ├── cache.py          # Gerenciamento de cache na memória para a API
│   │   ├── collector.py      # Lógica centralizada de coleta e distribuição de códigos
│   │   └── transformer.py    # Cálculos estatísticos e filtragem de períodos
│   ├── database/
│   │   ├── base.py           # Classe abstrata base (DataSource)
│   │   ├── bcb.py            # Adaptador para a API do Banco Central (SGS - SELIC)
│   │   └── ibge.py           # Adaptador para a API do IBGE (Agregados - IPCA)
│   ├── models/
│   │   ├── indicador.py      # Modelo de dados de um Indicador econômico
│   │   └── serie.py          # Modelo de dados de uma Série Histórica (com suporte a Pandas)
│   ├── routers/
│   │   └── router.py         # Mapeamento de rotas e lógica dos endpoints
│   ├── __init__.py
│   └── main.py               # Ponto de entrada e inicialização do FastAPI
├── dashboard.py              # Aplicação frontend interativa do Streamlit
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação do projeto
```

---

## 🛠️ Requisitos e Instalação

### Pré-requisitos
* Python 3.10 ou superior.

### Passos de Instalação

1. Clone ou acesse a pasta do repositório:
   ```bash
   cd econoapi
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Linux/macOS
   # ou: .venv\Scripts\activate  # No Windows
   ```

3. Instale as dependências exigidas:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Como Executar

O projeto pode ser rodado de duas formas independentes (ou ambas simultaneamente):

### 1. Executar o Dashboard Streamlit (Interface Visual)
Para abrir o painel interativo no navegador:
```bash
streamlit run dashboard.py
```
O Streamlit abrirá uma aba no navegador automaticamente no endereço local: **`http://localhost:8501`**.

### 2. Executar a API RESTful (FastAPI)
Para iniciar o servidor HTTP da API:
```bash
uvicorn app.main:app --reload
```
A API estará disponível em **`http://127.0.0.1:8000`**. Você pode acessar a documentação interativa automática do Swagger em **`http://127.0.0.1:8000/docs`**.

---

## 📊 Documentação da API REST

A API expõe as seguintes rotas sob o prefixo `/api`:

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | Retorna mensagem de boas-vindas ao sistema. |
| `GET` | `/api/indicadores` | Retorna o catálogo completo de indicadores disponíveis no coletor. |
| `GET` | `/api/dados/{fonte}/{codigo}` | Busca a série histórica real de uma fonte específica (Ex: `Banco do Brasil/11` ou `IBGE/1737`). |
| `GET` | `/api/dados/{fonte}/{codigo}/media` | Calcula e retorna a média aritmética simples dos valores da série no período. |

---

## ⚙️ Detalhes de Implementação e APIs Externas

### Banco Central do Brasil (SGS)
* **Indicador padrão**: Taxa SELIC (código `11`).
* **Endpoint de busca**: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json`
* **Tratamento**: A API do BCB possui uma restrição de no máximo 10 anos para dados diários. O sistema calcula dinamicamente uma janela de consulta do último ano (`dataInicial`) no formato de data brasileiro (`dd/mm/aaaa`), trata strings numéricas contendo vírgulas como separadores decimais e as tipifica como `float`.

### IBGE (Agregados)
* **Indicador padrão**: IPCA (código agregado `1737`).
* **Endpoint de busca**: `https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/-10/variaveis?localidades=BR`
* **Tratamento**: Filtra a lista de variáveis do agregado para extrair especificamente a variável ID `"63"` (que representa a *Variação Mensal do IPCA* / inflação oficial). Converte o formato do período de `YYYYMM` para `YYYY-MM` para correta ordenação cronológica e parseia os valores para `float`.
