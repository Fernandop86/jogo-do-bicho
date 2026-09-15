# Experimento de Machine Learning - Jogo do Bicho

**Data:** 2026-09-15
**Autor:** Fernando Pereira de Oliveira
**Objetivo:** Testar se Machine Learning consegue prever o proximo resultado.

---

## Sumario Executivo

**Conclusao:** Machine Learning **nao consegue** prever o proximo resultado do Jogo do Bicho.

Em **todos** os alvos testados (grupo, dezena, centena, milhar), a acuracia dos modelos foi **estatisticamente igual** ao aleatorio.

**Isso confirma** o que os testes chi2 ja mostravam: o jogo e **uniforme**.

---

## Metodologia

### Dados

| Fonte | Periodo | Linhas | Premios |
|-------|---------|--------|---------|
| jogo_do_bicho_2024.csv | 02/01 a 31/12/2024 | 2.066 | 10.325 |
| jogo_do_bicho_2026.csv | 02/01 a 14/09/2026 | 1.450 | 7.245 |
| **Total** | - | **3.516** | **17.570** |

### Features extraidas

Para cada sorteio, extraimos features do **historico anterior** (sem look-ahead):

- frequencia_acumulada - quantas vezes o valor apareceu ate agora
- atraso - quantos sorteios desde a ultima aparicao
- recencia_10 - aparicoes nos ultimos 10 sorteios
- recencia_30 - aparicoes nos ultimos 30 sorteios
- recencia_100 - aparicoes nos ultimos 100 sorteios
- foi_ultimo - apareceu no sorteio anterior?

### Validacao

- TimeSeriesSplit com 5 folds (validacao temporal, sem embaralhar)
- Treina nos primeiros N%, testa nos proximos
- Simula prever o futuro com base no passado

### Modelos

- Baseline aleatorio - chute uniforme
- Baseline mais frequente - chuta sempre a moda do treino
- Random Forest - 50 arvores, profundidade 10
- Regressao Logistica - multinomial, 500 iteracoes

---

## Resultados

### Tabela comparativa

| Alvo | Classes | Esperado (azar) | Aleatorio | Random Forest | Regressao Logistica | Melhor | Diferenca |
|------|---------|-----------------|-----------|---------------|---------------------|--------|-----------|
| Grupo | 25 | 4.0000% | 3.7400% | 3.8900% | 4.0400% | RL | +0.30 p.p. |
| Dezena | 100 | 1.0000% | 0.9631% | 0.9563% | 1.0861% | RL | +0.12 p.p. |
| Centena | 1.000 | 0.1000% | 0.0820% | 0.0888% | 0.0546% | RF | +0.01 p.p. |
| Milhar | 10.000 | 0.0100% | - | 0.0068% | - | RF | -0.003 p.p. |

### Interpretacao

- Diferencas menores que 0.5 p.p. sao ruido estatistico
- Nenhum alvo mostrou sinal exploravel
- Alguns modelos ficaram abaixo do aleatorio (overfitting)

---

## Estudo de Caso: Data Leakage

Durante o experimento com features exoticas (dia da semana, mes, modalidade),
observamos uma acuracia anomala de 8.15% (o dobro do aleatorio).

### Investigacao

A feature par_impar foi derivada do proprio target:

O bug estava em calcular par_impar a partir do valor (target),
fazendo o modelo usar a resposta para adivinhar a resposta.
Isso e data leakage classico.

### Correcao

Apos remover par_impar:

| Versao | Acuracia | Diferenca |
|--------|----------|-----------|
| Com leakage | 8.15% | +4.15 p.p. |
| Sem leakage | 4.02% | +0.01 p.p. |

Licao: acuracia muito acima do esperado e sinal de data leakage, nao de sucesso.

---

## Conclusao

### O que foi provado

1. ML nao consegue prever o proximo resultado
2. Nenhum alvo (grupo, dezena, centena, milhar) tem padrao exploravel
3. Features exoticas (dia, mes, modalidade) nao ajudam
4. O jogo e uniforme em todos os niveis

### Implicacoes

- Nao ha como ganhar dinheiro com ML neste jogo
- Qualquer sistema que prometa previsao esta mentindo
- Ciencia e isso: aceitar que o resultado e negativo

### Valor do experimento

Apesar do resultado negativo, o experimento:

- Confirma o que os testes chi2 ja mostravam
- Demonstra rigor cientifico (nao buscou confirmar vies)
- Documenta um caso real de data leakage
- Serve de referencia para quem quiser testar o mesmo

---

## Reproducao

    python ml_features.py --alvo grupo
    python ml_features.py --alvo dezena
    python ml_features.py --alvo centena
    python ml_features.py --alvo milhar

    python ml_modelos.py --alvo grupo
    python ml_modelos.py --alvo dezena
    python ml_modelos.py --alvo centena
    python ml_modelos.py --alvo milhar

    python ml_comparacao.py

    python ml_features_exoticas.py --alvo grupo
    python ml_modelos_exoticos.py --alvo grupo

---

## Referencias

- motor/estatistica_avancada.py - Testes chi2 e z-score
- docs/methodology.md - Metodologia da analise
- DISCLAIMER.md - Aviso legal

---

_Documento gerado em 2026-09-15._
