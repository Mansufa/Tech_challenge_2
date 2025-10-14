# TSP Solver — Genetic Algorithm (Python)

Uma implementação em Python de um solucionador para o problema do Caixeiro Viajante (TSP) usando Algoritmo Genético (GA) com visualização via Pygame.
![visualização do TSP](image.png)

## Visão geral
O projeto cria e evolui uma população de rotas (permutations de cidades) usando operadores típicos de GA (crossover do tipo order, mutação, elitismo), e exibe em tempo real a melhor solução encontrada usando Pygame. Ao final, os melhores resultados são salvos em `top50_results.csv` e `top50_results.json`.
## Estrutura principal

- `tsp.py` — script principal que inicializa o problema, roda a simulação/visualização e salva os resultados.
- `genetic_algorithm.py` — implementação do GA (geração, fitness, crossover, mutação, ordenação).
- `draw_functions.py` — funções auxiliares para desenhar cidades, rotas e gráfico usando Matplotlib + Pygame.
- `benchmark_att48.py` — dados do benchmark att48 (opcional).
## Dependências

- Python 3.10+ (testado aqui com Python 3.13)
- numpy
- pygame
- matplotlib
O repositório contém um `environment.yml` para criação de ambiente Conda; alternativamente você pode instalar com pip.

### Usando Conda (recomendado)
```bash
conda env create --file environment.yml
conda activate fiap_tsp
### Usando virtualenv / pip

```bash
python -m venv .venv
source .venv/bin/activate    # ou .venv\Scripts\activate no Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install --upgrade pip
pip install numpy pygame matplotlib
## Como executar

Abra um terminal no diretório do projeto e execute:
```bash
# usando o python do ambiente ativo
python tsp.py
Observações:
- O script abre uma janela do Pygame para visualização. Pressione a tecla `q` ou feche a janela para encerrar.
- Parâmetros importantes estão no topo de `tsp.py` e podem ser alterados:
  - `TIME_LIMIT_SECONDS` — tempo máximo de execução (padrão: 10 ou 120 conforme edição)
### Modos de problema

O `tsp.py` permite três modos (descomentar/ajustar no arquivo):
- Geração aleatória de cidades (recomendado para testes rápidos)
- Problemas pré-definidos (`default_problems` — 10, 12 ou 15 cidades)
- Benchmark `att48` (dados em `benchmark_att48.py`)
Por padrão você pode ativar a geração aleatória definindo `cities_locations` usando coordenadas randômicas (veja os comentários em `tsp.py`).

## Saída
Ao terminar a execução, o script salva automaticamente:

- `top50_results.csv` — CSV com os top 50 resultados (rank, generation, fitness, rota)
- `top50_results.json` — JSON estruturado com metadata e top results
Exemplo de uso programático: você pode ler `top50_results.json` para analisar os melhores trajetos e gerar imagens estáticas.

## Troubleshooting
- ModuleNotFoundError para `pygame` / `matplotlib` / `numpy`: instale as dependências conforme instruções acima.
- Se o Matplotlib reportar warnings de muitas figuras abertas, atualize `draw_functions.py` (já incluí uma chamada a `plt.close(fig)` para mitigar isso).
- Em ambientes sem display (servidores/CI) a janela do Pygame pode falhar; para rodar em modo "headless" você precisará adaptar `draw_functions.py` (gerar imagens sem abrir janela) ou usar um framebuffer virtual.
## Contribuições

Melhorias bem-vindas: parâmetros de seleção e recombinação, heurísticas iniciais (nearest neighbor), exportar imagem com a melhor rota, experimentos automatizados (benchmarks/variações de parâmetros).
## Licença

Este projeto está licenciado sob a MIT License — ver arquivo `LICENSE`.

---
Se quiser, eu atualizo o `tsp.py` para que ele ative automaticamente a geração aleatória de cidades (em vez do benchmark att48), e posso rodar o script por X segundos e mostrar os 5 melhores resultados do `top50_results.json`. Me diga o que prefere.
# TSP Solver using Genetic Algorithm

This repository contains a Python implementation of a Traveling Salesman Problem (TSP) solver using a Genetic Algorithm (GA). The TSP is a classic problem in the field of combinatorial optimization, where the goal is to find the shortest possible route that visits a set of given cities exactly once and returns to the original city.

![alt text](image.png)
![alt text](image-1.png)
## Prerequisites

- Download and Install conda environment manager.
  -  https://www.anaconda.com/download
- Open the `Anaconda Prompt`
- create the `fiap_tsp` environment
  - `conda env create --file environment.yml`
- activate the environment
  - `conda activate fiap_tsp`  

## How to Run

Execute the following command in your terminal to run the program:

### Pygame
# Otimização de Rotas Médicas — Algoritmo Genético (Python)

Este repositório implementa um sistema de otimização de rotas para entregas médicas usando um Algoritmo Genético (AG) com visualização em tempo de execução via Pygame.

![visualização](image.png)

## Visão geral
O objetivo é gerar rotas para uma frota de veículos que atendam entregas com diferentes prioridades (CRITICAL, HIGH, MEDIUM, LOW). O sistema permite configurar número de cidades, número de veículos e tempo máximo de execução via uma janela Pygame ao iniciar o programa.

Durante a execução o algoritmo evolui uma população de soluções e, ao final, salva as melhores soluções (PNG com mapa/rotas e CSV com rotas por veículo) em `src/images/`.

## Arquivos principais
- `main.py` — orquestra execução e UI (entrada via Pygame), loop do AG, desenho em tela e salvamento de artefatos (PNG/CSV).
- `population.py` — geração de população, cálculo de fitness, divisão de entregas entre veículos e otimizações locais (inclui garantia de prioridade nas rotas).
- `models.py` — modelos de dados (Delivery, Priority).
- `visualization.py` — funções de desenho e `draw_legend` (legenda é adicionada apenas nas imagens salvas).
- `config.py` — parâmetros e constantes do experimento.

## Saída gerada
- PNGs com as melhores soluções: `src/images/top_1.png` … `top_5.png`
- CSVs com rotas detalhadas por veículo: `src/images/top_1.csv` … `top_5.csv`
- Relatório técnico (MD e PDF): `REPORT_FASE2.md`, `REPORT_FASE2.pdf` (adicionados no branch)

Exemplo (trecho de `src/images/top_1.csv`):

```
SolutionRank,Fitness,VehicleID,DeliveryIDs,NumDeliveries,TotalWeight,Distance,Priorities
1,3489.46,1,4;0;1,3,48.36,679.5953541816605,CRITICAL;LOW;LOW
```

## Como executar
1. Ative o ambiente virtual (Windows):

```bash
.venv\Scripts\activate
```

2. Instale dependências (se necessário):

```bash
pip install -r requirements.txt
# ou instale individualmente: pip install pygame numpy matplotlib reportlab Pillow
```

3. Execute o programa principal:

```bash
python main.py
```

Ao abrir, a janela do Pygame pedirá: número de cidades, número de veículos e tempo de execução (segundos). Pressione Enter para aceitar o padrão.

## Relatório e documentação
O relatório da Fase 2 foi gerado e está disponível em `REPORT_FASE2.md` e `REPORT_FASE2.pdf`. Ele contém detalhes da implementação, resultados (imagens e CSVs) e recomendações para próximos passos.

## Dependências
- Python 3.10+ (testado com 3.13)
- numpy
- pygame
- matplotlib
- reportlab, Pillow (para geração de PDF)

Use `environment.yml` ou `requirements.txt` (se presente) para criar o ambiente.

## Observações e próximos passos
- As imagens e CSVs foram adicionadas ao repositório para facilitar revisão; se preferir, movemos `src/images/` para `.gitignore` para evitar poluição do histórico.
- Próximos passos recomendados:
  - Adicionar testes unitários para funções centrais (`population.py`).
  - Implementar heurísticas locais adicionais (2-opt) preservando priorização.
  - Gerar um CSV mestre agregando as 5 melhores soluções.

## Licença
MIT — veja `LICENSE`.

---

Se quiser que eu: (A) remova as imagens do controle de versão; (B) gere um release com o PDF; ou (C) adicione instruções de execução mais detalhadas (ex.: exemplos de parâmetros), me diga qual opção prefere.