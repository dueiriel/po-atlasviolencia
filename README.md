# Otimização de Recursos de Segurança Pública

**Trabalho Acadêmico de Pesquisa Operacional**

**Integrantes:**
- Pedro Lucas Dutra
- Davi Augusto Bitencourt de Souza

---

Trabalho acadêmico de **Pesquisa Operacional** que aplica **Programação Linear** para determinar a alocação ótima de recursos de segurança pública entre os estados brasileiros, com foco em identificar **quais estados investem de forma mais eficiente**.

## Objetivo Principal

> **Responder:** Quais estados brasileiros conseguem os melhores resultados em redução de violência por real investido, e como uma redistribuição otimizada de recursos poderia salvar mais vidas?

---

## Dados Utilizados

### Fontes Oficiais

| Fonte | Dados | Período | Link Direto |
|-------|-------|---------|-------------|
| **Atlas da Violência (IPEA/FBSP)** | Taxa de homicídios por UF | 1989-2022 | [ipea.gov.br/atlasviolencia](https://www.ipea.gov.br/atlasviolencia/dados-series/40) |
| **Anuário Brasileiro de Segurança Pública (FBSP)** | Mortes violentas por UF | 2021-2022 | [forumseguranca.org.br](https://forumseguranca.org.br/estatisticas/) |
| **SICONFI/Tesouro Nacional** | Gastos com Segurança Pública (Função 06) | 2013-2023 | [siconfi.tesouro.gov.br](https://siconfi.tesouro.gov.br/) |

### Origem dos Dados de Investimento

Os dados de **orçamento de segurança pública** vêm da **Tabela 54 do Anuário Brasileiro de Segurança Pública 2023**, que consolida as "Despesas realizadas com a Função Segurança Pública" de cada estado. A fonte primária é o SICONFI (Sistema de Informações Contábeis e Fiscais do Setor Público Brasileiro), que registra a execução orçamentária dos estados na Função 06 - Segurança Pública.

**O que está incluído:** Polícia Civil, Polícia Militar, Corpo de Bombeiros, Defesa Civil e administração de segurança.

**O que NÃO está incluído:** Gastos federais diretos (Polícia Federal, PRF), gastos municipais (guardas municipais).

📄 Documentação completa das fontes: [FONTES.md](FONTES.md)

---

## O Problema de Pesquisa Operacional

**Problema:** Dado um orçamento suplementar de R$ X bilhões, como distribuí-lo entre os 27 estados de forma a **minimizar o total de mortes violentas**?

### Formulação Matemática

**Variáveis de decisão:** 
- `x_i` = investimento adicional no estado i (R$ milhões)

**Função objetivo (minimizar mortes após investimento):**

```
Min Z = Σᵢ [ Cᵢ × (1 - εᵢ × xᵢ / Oᵢ) ]
```

Onde:
- `Cᵢ` = mortes violentas atuais no estado i
- `εᵢ` = elasticidade crime-investimento do estado i (calculada por regressão)
- `Oᵢ` = orçamento atual do estado i
- `xᵢ` = investimento adicional a alocar

**Restrições:**
```
Σᵢ xᵢ ≤ B                    (orçamento total disponível)
Lᵢ ≤ xᵢ ≤ Uᵢ    ∀i          (limites por estado)
xᵢ ≥ 0          ∀i          (não-negatividade)
```

**Método de solução:** Simplex (via PuLP + CBC solver)

---

## Conclusões Principais

### Estados Mais Eficientes (menor taxa relativa ao gasto)

Com base na análise do índice `(taxa média / taxa estado) / (gasto estado / gasto médio)`, os estados com **maior eficiência** no uso de recursos são:

| Ranking | Estado | Gasto/Capita | Taxa/100k | Índice de Eficiência |
|---------|--------|--------------|-----------|----------------------|
| 1º | São Paulo | R$ 334 | 54.8 | 2.82 |
| 2º | Distrito Federal | R$ 407 | 53.5 | 2.37 |
| 3º | Maranhão | R$ 304 | 71.6 | 2.37 |
| 4º | Piauí | R$ 306 | 80.8 | 2.09 |
| 5º | Santa Catarina | R$ 443 | 62.6 | 1.87 |

**Interpretação:** Estes estados conseguem taxas de violência abaixo da média com gastos abaixo da média nacional (R$ 633/capita).

### Estados Menos Eficientes (alto gasto, alta violência)

| Ranking | Estado | Gasto/Capita | Taxa/100k | Índice de Eficiência |
|---------|--------|--------------|-----------|----------------------|
| 27º | Tocantins | R$ 1.200 | 100.3 | 0.43 |
| 26º | Amapá | R$ 1.236 | 94.2 | 0.44 |
| 25º | Rondônia | R$ 1.013 | 101.1 | 0.50 |
| 24º | Roraima | R$ 996 | 96.0 | 0.54 |
| 23º | Mato Grosso | R$ 996 | 93.5 | 0.56 |

**Interpretação:** Estes estados gastam muito acima da média nacional mas mantêm taxas de violência altas, indicando ineficiência na aplicação dos recursos.

### Impacto da Otimização

Com orçamento suplementar de **R$ 5 bilhões** distribuídos de forma otimizada:

| Métrica | Valor |
|---------|-------|
| **Vidas potencialmente salvas** | ~1.875 |
| **Intervalo de confiança 95%** | [1.604 - 2.452] |
| **Custo médio por vida** | R$ 2,67 milhões |
| **Redução percentual de mortes** | 3,5% |

### Estados que Mais se Beneficiariam

Os estados com maior **elasticidade** (resposta ao investimento) e alta taxa de violência atual:

1. **Bahia** - maior número absoluto de mortes
2. **Pernambuco** - alta taxa + boa elasticidade
3. **Ceará** - terceiro maior impacto potencial
4. **Maranhão** - baixo gasto atual + alta elasticidade
5. **Rio de Janeiro** - alto volume de mortes evitáveis

---

## As 5 Abas da Aplicação

### 1. 📊 Dashboard
**O que mostra:** Panorama atual da segurança pública no Brasil.

- Mapa coroplético com taxa de violência por estado (escala de cores)
- Ranking de todos os 27 estados por taxa de mortes/100 mil hab.
- Mapa de calor e ranking de gasto per capita por estado
- Tabela completa com dados de todos os estados

**Como interpretar:** Estados com cores mais escuras no mapa têm maior taxa de violência.

### 2. ⚙️ Otimização
**O que faz:** Calcula a alocação ótima de um orçamento suplementar.

- Slider para definir orçamento total (R$ 1-20 bilhões)
- Limites mínimo/máximo de investimento por estado
- Botão "Calcular Alocação Ótima" executa o Simplex
- Exibe tabela com alocação ótima e comparativo antes/depois

**Como interpretar:** A tabela mostra quanto cada estado deve receber para maximizar vidas salvas dado o orçamento disponível.

### 3. 🎲 Monte Carlo
**O que faz:** Quantifica a incerteza via simulações estocásticas.

- Configurável: orçamento, número de simulações, incerteza nos parâmetros
- Botão "Executar Simulação Monte Carlo" para rodar
- Gera distribuição de possíveis resultados
- Calcula intervalo de confiança de 95%

**Como interpretar:** Se o IC 95% é [1.600, 2.400], significa que há 95% de chance de salvar entre 1.600 e 2.400 vidas.

### 4. 📅 Multi-Período
**O que analisa:** Planejamento para vários anos.

- Compara estratégias: Uniforme, Frontloaded, Backloaded, Crescente Linear
- Considera efeito acumulado dos investimentos
- Otimiza para 3-10 anos

**Como interpretar:** Frontloaded (investir mais cedo) geralmente ganha porque os benefícios se acumulam.

### 5. 📋 Conclusões
**O que apresenta:** Síntese final do estudo com análise DEA.

- **Análise de Eficiência DEA** (Data Envelopment Analysis)
  - Pesos: 75% Resultado (baixa taxa de homicídios) + 25% Economia (baixo gasto)
- Ranking completo de eficiência de todos os estados
- Principais conclusões e insights

---

## Instalação

```bash
git clone https://github.com/dueiriel/po-atlasviolencia.git
cd po-atlasviolencia

python -m venv venv
source venv/bin/activate   # Linux/Mac
# ou: venv\Scripts\activate  # Windows

pip install -r requirements.txt
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

---

## Estrutura do Projeto

```
├── app.py                    # Interface Streamlit (5 abas)
├── dados.py                  # Carregamento e processamento de dados
├── otimizacao.py             # Modelo de Programação Linear (PuLP/CBC)
├── dea.py                    # Análise de Eficiência DEA
├── monte_carlo.py            # Simulação estocástica (otimizada)
├── multi_periodo.py          # Otimização em múltiplos períodos
├── requirements.txt          # Dependências Python
├── FONTES.md                 # Documentação detalhada das fontes
├── latex/                    # Documento LaTeX do trabalho
│   └── trabalho_po.tex
└── dados/
    ├── taxa_homicidios_jovens.csv    # IPEA: série 1989-2022
    ├── mortes_populacao_2022.csv     # IPEA: MVI e população 2022
    ├── mortes_violentas_2022.csv     # FBSP: mortes por UF 2022
    └── dados.novos/                  # SICONFI: gastos 2013-2023
        ├── gastos_2013_filtrado.csv
        ├── ...
        └── gastos_2023_filtrado.csv
```

---

## Limitações do Modelo

1. **Elasticidade é uma simplificação:** A relação real entre gasto e crime depende de como o dinheiro é aplicado (tecnologia, efetivo, inteligência).

2. **Dados de orçamento limitados:** Só temos 2021-2022 no Anuário FBSP. Séries mais longas permitiriam elasticidades mais precisas.

3. **Tocantins:** Não encontrado na tabela do FBSP. Usamos a média da região Norte como proxy.

4. **Linearidade:** O modelo assume que dobrar o investimento dobra o efeito, o que provavelmente não vale para investimentos muito grandes (retornos decrescentes).

5. **Fatores externos:** O modelo não captura mudanças estruturais (legislação, demografia, economia).

---

## Referências Bibliográficas

### Pesquisa Operacional
- Winston, W. L. (2003). *Operations Research: Applications and Algorithms*. 4th ed. Duxbury.
- Hillier, F. S.; Lieberman, G. J. (2015). *Introduction to Operations Research*. 10th ed. McGraw-Hill.
- Taha, H. A. (2017). *Operations Research: An Introduction*. 10th ed. Pearson.

### Simulação e Estatística
- Rubinstein, R. Y.; Kroese, D. P. (2016). *Simulation and the Monte Carlo Method*. 3rd ed. Wiley.
- Law, A. M. (2014). *Simulation Modeling and Analysis*. 5th ed. McGraw-Hill.

### Economia do Crime
- Becker, G. S. (1968). "Crime and Punishment: An Economic Approach". *Journal of Political Economy*, 76(2).
- Cerqueira, D. (2014). *Causas e consequências do crime no Brasil*. BNDES.

---

## Licença

Projeto acadêmico para fins educacionais.

---

*Desenvolvido como trabalho de Pesquisa Operacional - 2026*

## .