# 🔐 Otimização de Recursos de Segurança Pública

## Trabalho Acadêmico - Pesquisa Operacional

Aplicação que utiliza **Programação Linear** para otimizar a alocação de recursos de segurança pública entre diferentes estados brasileiros, com base em dados do Atlas da Violência.

## 🎯 Objetivo

Determinar a alocação ideal de verba suplementar para **minimizar a taxa global de crimes**, assumindo que o investimento reduz o crime com base em uma eficiência histórica.

## 🧮 Modelo Matemático

### Variáveis de Decisão
- `x_i`: Investimento adicional no estado `i` (em R$ milhões)

### Função Objetivo
Minimizar a soma ponderada de crimes esperados após investimento:

```
Min Σ (TaxaCrime_i × População_i × (1 - Elasticidade_i × x_i / Orçamento_i))
```

### Restrições
1. Orçamento total: `Σ x_i ≤ OrçamentoDisponível`
2. Investimento mínimo: `x_i ≥ InvestMin_i`
3. Investimento máximo: `x_i ≤ InvestMax_i`

## 🚀 Como Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

## 📊 Funcionalidades

- **Dashboard**: Mapa de calor do Brasil com dados atuais
- **Otimização**: Slider para definir orçamento e calcular alocação ótima
- **Comparativo**: Gráfico "Antes vs. Depois" da otimização
- **Explicação**: Seção educacional sobre o modelo de PO utilizado

## 📚 Referências

- Atlas da Violência - IPEA
- Orçamentos estaduais de Segurança Pública
