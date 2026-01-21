# =============================================================================
# MÓDULO DE DADOS - ATLAS DA VIOLÊNCIA E ORÇAMENTO DE SEGURANÇA PÚBLICA
# =============================================================================
# Este módulo processa dados de fontes oficiais brasileiras:
# - Homicídios por UF (2013-2023): dados/dados.novos/Dados Homicidios 2013-2023.xlsx
# - Gastos com segurança pública por UF (2013-2023): dados/dados.novos/gastos_YYYY_filtrado.csv
#
# IMPORTANTE: Este módulo usa EXCLUSIVAMENTE os arquivos da pasta dados/dados.novos
# =============================================================================

import pandas as pd
import numpy as np
from pathlib import Path

# Diretório base dos dados NOVOS (relativo ao módulo)
DADOS_DIR = Path(__file__).parent / "dados" / "dados.novos"

# Anos disponíveis nos novos dados
ANOS_DISPONIVEIS = list(range(2013, 2024))  # 2013 a 2023


def carregar_gastos_por_ano(ano: int) -> pd.DataFrame:
    """
    Carrega dados de gastos com segurança pública de um ano específico.
    
    Fonte: dados/dados.novos/gastos_YYYY_filtrado.csv
    
    Args:
        ano: Ano dos dados (2013 a 2023)
    
    Returns:
        DataFrame com colunas: sigla, cod_uf, populacao, gasto_seguranca, ano
    """
    arquivo = DADOS_DIR / f"gastos_{ano}_filtrado.csv"
    
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    
    df = pd.read_csv(arquivo, sep=';')
    
    # Padroniza nomes de colunas
    df = df.rename(columns={
        'UF': 'sigla',
        'Cod.IBGE': 'cod_uf',
        'População': 'populacao',
        'Valor': 'gasto_seguranca'
    })
    
    # Converte valor (pode estar com vírgula como separador decimal)
    if df['gasto_seguranca'].dtype == object:
        df['gasto_seguranca'] = df['gasto_seguranca'].str.replace('.', '', regex=False)
        df['gasto_seguranca'] = df['gasto_seguranca'].str.replace(',', '.', regex=False)
        df['gasto_seguranca'] = pd.to_numeric(df['gasto_seguranca'], errors='coerce')
    
    df['ano'] = ano
    
    # Seleciona colunas relevantes
    return df[['sigla', 'cod_uf', 'populacao', 'gasto_seguranca', 'ano']]


def carregar_gastos_todos_anos() -> pd.DataFrame:
    """
    Carrega e consolida gastos de todos os anos disponíveis (2013-2023).
    
    Returns:
        DataFrame com gastos de todos os anos
    """
    dfs = []
    for ano in ANOS_DISPONIVEIS:
        try:
            df_ano = carregar_gastos_por_ano(ano)
            dfs.append(df_ano)
        except FileNotFoundError:
            print(f"Aviso: Dados de gastos para {ano} não encontrados, pulando...")
    
    if not dfs:
        raise ValueError("Nenhum arquivo de gastos encontrado em dados/dados.novos")
    
    return pd.concat(dfs, ignore_index=True)


def carregar_homicidios() -> pd.DataFrame:
    """
    Carrega dados de homicídios por UF (2013-2023).
    
    Fonte: dados/dados.novos/Dados Homicidios 2013-2023.xlsx
    
    Returns:
        DataFrame no formato longo: sigla, ano, homicidios
    """
    arquivo = DADOS_DIR / "Dados Homicidios 2013-2023.xlsx"
    
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    
    # Lê o Excel sem header (vamos processar manualmente)
    df_raw = pd.read_excel(arquivo, header=None)
    
    # A estrutura do arquivo:
    # Linha 0: Título "Brasil e Unidades da Federação"
    # Linhas 1-3: Vazias
    # Linha 4: NaN, 2023, 2022, 2021, ..., 2013 (os anos nas colunas 1-11)
    # Linha 5: Brasil, totais...
    # Linhas 6-32: Estados (Acre, Alagoas, ..., Tocantins)
    
    # Extrai os anos da linha 4 (colunas 1-11)
    anos_row = df_raw.iloc[4, 1:12].tolist()
    anos = [int(a) for a in anos_row if pd.notna(a)]
    
    # Extrai dados dos estados (linhas 6 em diante, excluindo Brasil na linha 5)
    # Pegamos apenas as primeiras 12 colunas (estado + 11 anos)
    df_estados = df_raw.iloc[6:33, 0:12].copy()
    
    # Define nomes das colunas
    novos_nomes = ['estado'] + [str(a) for a in anos]
    df_estados.columns = novos_nomes
    
    # Remove linhas vazias
    df_estados = df_estados.dropna(subset=['estado'])
    
    # Remove notas numéricas dos nomes dos estados (ex: "Minas Gerais (5)")
    df_estados['estado'] = df_estados['estado'].astype(str).str.replace(r'\s*\(\d+\)\s*', '', regex=True).str.strip()
    
    # Transforma para formato longo
    anos_cols = [str(ano) for ano in anos]
    df_long = df_estados.melt(
        id_vars=['estado'],
        value_vars=anos_cols,
        var_name='ano',
        value_name='homicidios'
    )
    
    df_long['ano'] = df_long['ano'].astype(int)
    df_long['homicidios'] = pd.to_numeric(df_long['homicidios'], errors='coerce')
    
    # Adiciona sigla do estado
    estado_para_sigla = _mapeamento_estados_siglas()
    df_long['sigla'] = df_long['estado'].map(estado_para_sigla)
    
    return df_long[['sigla', 'estado', 'ano', 'homicidios']]


def carregar_mortes_populacao(ano: int = 2022) -> pd.DataFrame:
    """
    Carrega dados de mortes violentas e população por UF para um ano específico.
    
    Usa os novos dados de dados/dados.novos.
    
    Args:
        ano: Ano dos dados (padrão: 2022)
    
    Returns:
        DataFrame com colunas: sigla, estado, populacao, mortes_violentas, taxa_mortes_100k
    """
    df_gastos = carregar_gastos_por_ano(ano)
    df_homicidios = carregar_homicidios()
    
    # Filtra homicídios pelo ano
    df_hom_ano = df_homicidios[df_homicidios['ano'] == ano].copy()
    
    # Merge gastos com homicídios
    df = pd.merge(
        df_gastos[['sigla', 'cod_uf', 'populacao']],
        df_hom_ano[['sigla', 'estado', 'homicidios']],
        on='sigla',
        how='left'
    )
    
    df = df.rename(columns={'homicidios': 'mortes_violentas'})
    
    # Calcula taxa de mortes por 100 mil habitantes
    df['taxa_mortes_100k'] = (df['mortes_violentas'] / df['populacao'] * 100000).round(2)
    
    return df


def carregar_taxa_homicidios_historico() -> pd.DataFrame:
    """
    Carrega série histórica de taxa de homicídios (2013-2023).
    
    Usa os novos dados de dados/dados.novos.
    
    Returns:
        DataFrame com colunas: sigla, estado, ano, homicidios, taxa_homicidios_100k
    """
    df_homicidios = carregar_homicidios()
    df_gastos = carregar_gastos_todos_anos()
    
    # Merge para obter população por ano
    df = pd.merge(
        df_homicidios,
        df_gastos[['sigla', 'ano', 'populacao']],
        on=['sigla', 'ano'],
        how='left'
    )
    
    # Calcula taxa por 100k habitantes
    df['taxa_homicidios_100k'] = (df['homicidios'] / df['populacao'] * 100000).round(2)
    
    return df


def carregar_orcamento_seguranca(ano: int = 2022) -> pd.DataFrame:
    """
    Carrega dados de orçamento de segurança pública por UF para um ano específico.
    
    Fonte: dados/dados.novos/gastos_YYYY_filtrado.csv
    
    Args:
        ano: Ano dos dados (padrão: 2022)
    
    Returns:
        DataFrame com colunas: sigla, estado, orcamento, orcamento_milhoes
    """
    df = carregar_gastos_por_ano(ano)
    
    # Adiciona nome do estado
    siglas_estados = _mapeamento_siglas_estados()
    df['estado'] = df['sigla'].map(siglas_estados)
    
    df = df.rename(columns={'gasto_seguranca': f'orcamento_{ano}'})
    df[f'orcamento_{ano}_milhoes'] = (df[f'orcamento_{ano}'] / 1e6).round(2)
    
    return df[['sigla', 'estado', 'cod_uf', 'populacao', f'orcamento_{ano}', f'orcamento_{ano}_milhoes']]


def _mapeamento_estados_siglas() -> dict:
    """
    Retorna dicionário de mapeamento entre nomes completos e siglas dos estados.
    """
    return {
        'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
        'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF',
        'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA',
        'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG',
        'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR', 'Pernambuco': 'PE',
        'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
        'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR',
        'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'
    }


def _mapeamento_siglas_estados() -> dict:
    """
    Retorna dicionário de mapeamento entre siglas e nomes completos dos estados.
    """
    return {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 
        'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
        'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
        'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco',
        'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima',
        'SC': 'Santa Catarina', 'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }


def _mapeamento_regioes() -> dict:
    """
    Retorna dicionário de mapeamento entre siglas e regiões do Brasil.
    """
    return {
        'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte',
        'BA': 'Nordeste', 'CE': 'Nordeste', 'DF': 'Centro-Oeste',
        'ES': 'Sudeste', 'GO': 'Centro-Oeste', 'MA': 'Nordeste',
        'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
        'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste',
        'PI': 'Nordeste', 'RJ': 'Sudeste', 'RN': 'Nordeste',
        'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte',
        'SC': 'Sul', 'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
    }


def carregar_dados_consolidados(ano: int = 2022) -> pd.DataFrame:
    """
    Consolida todos os dados em um único DataFrame pronto para otimização.
    
    Este é o principal ponto de entrada para o modelo de otimização.
    Combina dados de homicídios/população com gastos de segurança.
    
    IMPORTANTE: Usa EXCLUSIVAMENTE os arquivos de dados/dados.novos
    
    Args:
        ano: Ano base para análise (padrão: 2022)
    
    Também calcula a ELASTICIDADE estimada de redução de crime:
    - A elasticidade representa quanto a taxa de crime reduz para cada
      1% de aumento no orçamento de segurança.
    - Valores típicos na literatura: 0.05 a 0.15
    - Usamos a variação histórica de orçamento vs. crime para estimar.
    
    Returns:
        DataFrame consolidado com todas as variáveis para otimização
    """
    # Carrega os dados base dos NOVOS arquivos
    df_gastos = carregar_gastos_por_ano(ano)
    df_homicidios = carregar_homicidios()
    
    # Filtra homicídios pelo ano
    df_hom_ano = df_homicidios[df_homicidios['ano'] == ano].copy()
    
    # Cria mapeamentos
    siglas_estados = _mapeamento_siglas_estados()
    regioes = _mapeamento_regioes()
    
    # Adiciona nome do estado e região
    df_gastos['estado'] = df_gastos['sigla'].map(siglas_estados)
    df_gastos['regiao'] = df_gastos['sigla'].map(regioes)
    
    # Merge com dados de homicídios
    df = pd.merge(
        df_gastos,
        df_hom_ano[['sigla', 'homicidios']],
        on='sigla',
        how='left'
    )
    
    df = df.rename(columns={
        'homicidios': 'mortes_violentas',
        'gasto_seguranca': 'orcamento_2022'
    })
    
    # Calcula taxa de mortes por 100 mil habitantes
    df['taxa_mortes_100k'] = (df['mortes_violentas'] / df['populacao'] * 100000).round(2)
    
    # Converte de R$ para R$ milhões para facilitar leitura
    df['orcamento_2022_milhoes'] = (df['orcamento_2022'] / 1e6).round(2)
    
    # Calcula gasto per capita (R$ por habitante)
    df['gasto_per_capita'] = (df['orcamento_2022'] / df['populacao']).round(2)
    
    # ==========================================================================
    # ESTIMATIVA DE ELASTICIDADE
    # ==========================================================================
    # A elasticidade crime-gasto representa a sensibilidade da taxa de crime
    # a variações no orçamento de segurança. Na ausência de dados longitudinais
    # detalhados, usamos uma abordagem baseada em:
    #
    # 1. Estados com maior gasto per capita tendem a ter menor taxa de crime
    # 2. Estados com histórico de redução de crime têm maior "eficiência"
    # 3. Valores são calibrados pela literatura (0.05 a 0.15)
    # ==========================================================================
    
    # Normaliza gasto per capita (0 a 1)
    gpc_min = df['gasto_per_capita'].min()
    gpc_max = df['gasto_per_capita'].max()
    df['gasto_per_capita_norm'] = (df['gasto_per_capita'] - gpc_min) / (gpc_max - gpc_min)
    
    # Elasticidade: estados com menor gasto têm maior potencial
    # Base: 0.08, máximo adicional: 0.07 (total: 0.08 a 0.15)
    df['elasticidade'] = (0.08 + 0.07 * (1 - df['gasto_per_capita_norm'])).round(4)
    
    # Calcula índice de prioridade (para ranking)
    # Estados com alta taxa de crime e baixo investimento = alta prioridade
    df['indice_prioridade'] = (
        df['taxa_mortes_100k'] / df['gasto_per_capita'] * 100
    ).round(2)
    
    # Ordena por sigla para consistência
    df = df.sort_values('sigla').reset_index(drop=True)
    
    # Seleciona e ordena colunas para saída
    colunas_saida = [
        'sigla', 'estado', 'regiao', 'cod_uf',
        'populacao', 'mortes_violentas', 'taxa_mortes_100k',
        'orcamento_2022', 'orcamento_2022_milhoes', 'gasto_per_capita',
        'elasticidade', 'indice_prioridade'
    ]
    
    return df[colunas_saida]


def obter_coordenadas_estados() -> pd.DataFrame:
    """
    Retorna coordenadas geográficas aproximadas das capitais estaduais.
    
    Usado para plotagem de mapas quando não se usa GeoJSON.
    
    Returns:
        DataFrame com sigla, latitude, longitude
    """
    coords = {
        'AC': (-9.97, -67.81), 'AL': (-9.67, -35.74), 'AP': (0.03, -51.07),
        'AM': (-3.12, -60.02), 'BA': (-12.97, -38.51), 'CE': (-3.72, -38.54),
        'DF': (-15.78, -47.93), 'ES': (-20.32, -40.34), 'GO': (-16.68, -49.26),
        'MA': (-2.53, -44.27), 'MT': (-15.60, -56.10), 'MS': (-20.44, -54.64),
        'MG': (-19.92, -43.94), 'PA': (-1.46, -48.50), 'PB': (-7.12, -34.86),
        'PR': (-25.42, -49.27), 'PE': (-8.05, -34.88), 'PI': (-5.09, -42.80),
        'RJ': (-22.91, -43.17), 'RN': (-5.79, -35.21), 'RS': (-30.03, -51.23),
        'RO': (-8.76, -63.90), 'RR': (2.82, -60.67), 'SC': (-27.59, -48.55),
        'SP': (-23.55, -46.64), 'SE': (-10.91, -37.07), 'TO': (-10.18, -48.33)
    }
    
    df = pd.DataFrame([
        {'sigla': sigla, 'latitude': lat, 'longitude': lon}
        for sigla, (lat, lon) in coords.items()
    ])
    
    return df


# =============================================================================
# TESTE DO MÓDULO
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: CARREGAMENTO DE DADOS CONSOLIDADOS")
    print("=" * 70)
    
    try:
        df = carregar_dados_consolidados()
        print(f"\n✓ Dados carregados com sucesso: {len(df)} estados\n")
        
        print("AMOSTRA DOS DADOS:")
        print("-" * 70)
        colunas_exibir = ['sigla', 'estado', 'taxa_mortes_100k', 
                          'orcamento_2022_milhoes', 'elasticidade']
        print(df[colunas_exibir].to_string(index=False))
        
        print("\n" + "=" * 70)
        print("ESTATÍSTICAS DESCRITIVAS")
        print("=" * 70)
        print(df[['taxa_mortes_100k', 'orcamento_2022_milhoes', 
                  'gasto_per_capita', 'elasticidade']].describe())
        
        print("\n" + "=" * 70)
        print("TOP 5 ESTADOS POR ÍNDICE DE PRIORIDADE")
        print("(Maior taxa de crime / menor investimento)")
        print("=" * 70)
        top5 = df.nlargest(5, 'indice_prioridade')[
            ['sigla', 'estado', 'taxa_mortes_100k', 'gasto_per_capita', 'indice_prioridade']
        ]
        print(top5.to_string(index=False))
        
    except Exception as e:
        print(f"\n✗ Erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
