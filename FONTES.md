# Fontes de Dados - Documentação Completa

Este documento descreve em detalhes todas as fontes de dados utilizadas neste projeto, incluindo links diretos para download, metodologia de coleta e limitações conhecidas.

---

## 1. Dados de Violência

### 1.1 Homicídios por UF (2013-2023)

**O que é:** Dados de homicídios consolidados por Unidade da Federação, extraídos de fontes oficiais brasileiras.

**Dados utilizados:**
- Número absoluto de homicídios por UF: 2013-2023

**Fonte primária:** Sistema de Informação sobre Mortalidade (SIM) do Ministério da Saúde, via DATASUS.

**Arquivo no projeto:** `dados/dados.novos/Dados Homicidios 2013-2023.xlsx`

**Observação:** Os dados incluem homicídios dolosos (classificação CID-10: X85-Y09, Y35-Y36).

---

## 2. Dados de Orçamento/Gastos em Segurança Pública

### 2.1 SICONFI - Sistema de Informações Contábeis e Fiscais (2013-2023)

**O que é:** Sistema da Secretaria do Tesouro Nacional que centraliza dados contábeis e fiscais de todos os entes da federação.

**Dados utilizados:**
- Despesas Liquidadas com a Função 06 (Segurança Pública) por UF
- Período: 2013 a 2023 (11 anos de dados)
- Valores em R$ correntes do respectivo ano

**Fonte:**
- Portal SICONFI: https://siconfi.tesouro.gov.br/
- Relatórios: Demonstrativo de Despesas por Função/Subfunção

**Arquivos no projeto:** 
```
dados/dados.novos/
├── gastos_2013_filtrado.csv
├── gastos_2014_filtrado.csv
├── gastos_2015_filtrado.csv
├── gastos_2016_filtrado.csv
├── gastos_2017_filtrado.csv
├── gastos_2018_filtrado.csv
├── gastos_2019_filtrado.csv
├── gastos_2020_filtrado.csv
├── gastos_2021_filtrado.csv
├── gastos_2022_filtrado.csv
└── gastos_2023_filtrado.csv
```

**O que está incluído na Função 06 - Segurança Pública:**
- Policiamento
- Defesa Civil
- Informação e Inteligência
- Administração de Segurança Pública

**O que NÃO está incluído:**
- Gastos federais diretos (Polícia Federal, Polícia Rodoviária Federal)
- Gastos municipais (Guardas Municipais)
- Sistema prisional (Função 14 - Direitos da Cidadania)

---

## 3. Dados Demográficos

### 3.1 População por UF

**Fonte:** Os dados de população estão incluídos nos arquivos de gastos do SICONFI.

**Dados utilizados:** População estimada por UF em cada ano (2013-2023)

---

## 4. Dados Geográficos

### 4.1 GeoJSON dos Estados Brasileiros

**Fonte:** Repositório "Click That Hood" (dados originais do IBGE)
- URL: https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson

**Uso:** Mapa coroplético do Brasil na aba Dashboard

---

## 5. Processamento e Transformações

### 5.1 Cálculo da Taxa de Mortes por 100 mil habitantes

```
taxa_mortes_100k = (homicidios / populacao) × 100.000
```

### 5.2 Cálculo do Gasto Per Capita

```
gasto_per_capita = gasto_seguranca / populacao
```

### 5.3 Cálculo da Elasticidade

A elasticidade crime-investimento mede a sensibilidade da taxa de homicídios a variações no gasto com segurança. É calculada usando regressão linear sobre a série histórica:

```python
# Para cada estado, usando dados de 2013-2023
elasticidade = coeficiente da regressão Δ_taxa_homicidios ~ Δ_gasto
```

### 5.4 Cálculo da Eficiência (DEA)

Utilizamos modelo inspirado em DEA (Data Envelopment Analysis) com pesos fixos:

```
Eficiência = 0,75 × (Taxa_min / Taxa_estado) + 0,25 × (Gasto_min / Gasto_estado)
```

Onde:
- **75%** do peso é dado ao **resultado** (quanto menor a taxa de homicídios, melhor)
- **25%** do peso é dado à **economia** (quanto menor o gasto per capita, melhor)

---

## 6. Referências Acadêmicas

### Pesquisa Operacional e Programação Linear
- Winston, W. L. (2003). *Operations Research: Applications and Algorithms*. 4th ed. Duxbury Press.
- Hillier, F. S.; Lieberman, G. J. (2015). *Introduction to Operations Research*. 10th ed. McGraw-Hill.

### Simulação Monte Carlo
- Rubinstein, R. Y.; Kroese, D. P. (2016). *Simulation and the Monte Carlo Method*. 3rd ed. Wiley.

### Economia do Crime
- Becker, G. S. (1968). "Crime and Punishment: An Economic Approach". *Journal of Political Economy*, 76(2), 169-217.

### DEA (Data Envelopment Analysis)
- Charnes, A.; Cooper, W. W.; Rhodes, E. (1978). "Measuring the efficiency of decision making units". *European Journal of Operational Research*, 2(6), 429-444.
