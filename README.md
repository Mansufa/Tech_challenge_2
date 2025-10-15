# Tech Challenge - Fase 2: Otimização de Rotas Médicas com Algoritmos Genéticos
## Links:
Repositório -> https://github.com/Mansufa/Tech_challenge_2

Video apresentação -> https://www.youtube.com/watch?v=B4m42YhCTao


## 1. Descrição do Projeto

O objetivo deste projeto é desenvolver um sistema de otimização de rotas para a distribuição de medicamentos e insumos de um hospital. O sistema utiliza Algoritmos Genéticos para resolver um Problema de Roteamento de Veículos (VRP) complexo, considerando múltiplas restrições do mundo real, como capacidade de carga, número máximo de entregas por veículo e prioridades variadas para cada entrega. A solução busca minimizar a distância total percorrida pela frota, ao mesmo tempo que respeita todas as restrições operacionais, garantindo eficiência e urgência.

## 2. Tecnologias Utilizadas

*   **Python 3.11+:** Linguagem principal para o desenvolvimento de toda a lógica.
*   **Pygame:** Biblioteca utilizada para criar a interface gráfica interativa, permitindo a visualização em tempo real do processo de otimização e a entrada de parâmetros pelo usuário.
*   **NumPy:** Utilizada para cálculos numéricos eficientes, especialmente na manipulação de probabilidades para a seleção de indivíduos no algoritmo genético.
*   **Pipenv:** Ferramenta para gerenciamento de dependências e ambientes virtuais, garantindo a reprodutibilidade do ambiente de desenvolvimento.

## 3. Instalação e Execução

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

1.  **Instale as dependências:**
    O `Pipfile` no projeto garante que as dependências corretas sejam instaladas. Execute o comando:
    ```bash
    pipenv install
    ```

2.  **Execute o projeto:**
    Para iniciar a aplicação, utilize o seguinte comando, que ativa o ambiente virtual e executa o script principal:
    ```bash
    pipenv run python src/main.py
    ```

## 4. Arquitetura do Projeto

O projeto foi estruturado de forma modular para separar as responsabilidades e facilitar a manutenção. Os principais módulos no diretório `src/` são:

*   **[`main.py`](src/main.py):** Ponto de entrada e orquestrador principal. É responsável por inicializar o Pygame, obter os parâmetros do usuário, controlar o loop principal do Algoritmo Genético e salvar os resultados finais.
*   **[`models.py`](src/models.py):** Define as estruturas de dados centrais do projeto, como a classe `Delivery` para representar uma entrega e o enum `Priority` para os níveis de prioridade.
*   **[`config.py`](src/config.py):** Centraliza todas as constantes e parâmetros configuráveis, como o tamanho da população, taxa de mutação, penalidades e cores para visualização.
*   **[`population.py`](src/population.py):** Contém a lógica essencial do VRP, incluindo a criação da população inicial, a complexa função de cálculo de fitness e a estratégia para dividir uma lista de entregas entre os múltiplos veículos.
*   **[`genetic_operators.py`](src/genetic_operators.py):** Implementa as funções puras do Algoritmo Genético: Seleção (implícita no loop principal), Crossover (`order_crossover`) e Mutação (`swap_mutation`).
*   **[`visualization.py`](src/visualization.py):** Agrupa todas as funções responsáveis por desenhar os elementos na tela com Pygame, como o depósito, as entregas, as rotas dos veículos e o gráfico de evolução do fitness.

## 5. Implementação do Algoritmo Genético

### 5.1. Codificação (Representação do Indivíduo)

Um "indivíduo" na população representa uma solução candidata completa para o problema. Ele é codificado como uma lista única contendo a sequência (permutação) de todos os objetos `Delivery` a serem realizados. Essa representação linear é ideal para a aplicação de operadores genéticos como o crossover de ordem. Posteriormente, a função [`split_deliveries_by_vehicle`](src/population.py) processa essa lista para dividi-la de forma inteligente entre os veículos disponíveis, gerando as rotas individuais que serão avaliadas.

### 5.2. Função Fitness e Restrições

A função fitness, implementada em [`calculate_fitness_multi_vehicle`](src/population.py), é o coração do algoritmo e avalia a qualidade de cada indivíduo. Ela vai além da simples distância, incorporando um sistema de penalidades para garantir que as soluções evoluam em direção ao cumprimento de todas as restrições do problema. A fórmula geral é: *Fitness = Distância Total + Penalidade de Carga + Penalidade de Prioridade*.

*   **Múltiplos Veículos:** A lista de entregas do indivíduo é dividida entre os veículos pela função [`split_deliveries_by_vehicle`](src/population.py). Essa função primeiro ordena as entregas por prioridade e depois as atribui ao veículo com menor carga atual que ainda possua capacidade de peso e de número de entregas.
*   **Capacidade de Carga:** Se a soma dos pesos das entregas em uma rota excede a capacidade do veículo correspondente, uma penalidade (`PENALTY_OVERLOAD`) é adicionada ao fitness. A magnitude da penalidade é proporcional à porcentagem de sobrecarga, desencorajando fortemente soluções inválidas.
*   **Autonomia do Veículo:** Embora não haja uma penalidade explícita para autonomia, a própria função fitness busca minimizar a distância total percorrida (`total_distance`). Ao otimizar a distância de cada rota, o algoritmo indiretamente favorece soluções que consomem menos "autonomia".
*   **Prioridade de Entregas:** A prioridade é tratada de duas formas:
    1.  **Na divisão de rotas:** A função [`optimize_route_respecting_priority`](src/population.py) organiza as entregas dentro da rota de cada veículo para que os grupos de maior prioridade (CRITICAL, HIGH) sejam atendidos antes dos de menor prioridade.
    2.  **Na função fitness:** Uma penalidade (`PENALTY_PRIORITY`) é aplicada se entregas de alta prioridade aparecem muito tarde na sequência geral de entregas do indivíduo, garantindo que o algoritmo aprenda a posicioná-las no início.

### 5.3. Operadores Genéticos

*   **Seleção:** O algoritmo utiliza uma combinação de **Elitismo**, onde o melhor indivíduo da geração atual é garantido na próxima, e **Seleção por Roleta**, onde os pais são escolhidos aleatoriamente com uma probabilidade inversamente proporcional ao seu fitness (indivíduos melhores têm mais chances de serem escolhidos).
*   **Crossover:** Foi utilizado o **Ordered Crossover (OX1)**, implementado em [`order_crossover`](src/genetic_operators.py). Este operador é especialmente adequado para problemas de permutação, como o VRP, pois garante que o filho gerado seja sempre uma permutação válida das entregas, sem duplicatas ou omissões.
*   **Mutação:** A **Swap Mutation** (mutação por troca), implementada em [`swap_mutation`](src/genetic_operators.py), é aplicada com uma probabilidade definida em [`MUTATION_PROBABILITY`](src/config.py). Ela troca a posição de duas entregas adjacentes na lista, introduzindo pequenas variações nas rotas e ajudando o algoritmo a escapar de mínimos locais.

## 6. Resultados e Análise

### 6.1. Visualização

A interface gráfica desenvolvida com Pygame oferece uma visão clara e em tempo real da performance do algoritmo. A tela principal exibe:
*   **Pontos de Entrega:** Círculos coloridos que representam as entregas, com a cor indicando a prioridade (ex: vermelho para CRÍTICO).
*   **Rotas dos Veículos:** Linhas de cores distintas conectam o depósito e os pontos de entrega, mostrando a rota otimizada para cada veículo na melhor solução da geração atual.
*   **Gráfico de Evolução:** Um gráfico no canto superior esquerdo mostra a queda do valor do fitness (eixo Y) ao longo das gerações (eixo X), ilustrando visualmente o aprendizado e a convergência do algoritmo.

### 6.2. Análise de Desempenho

A eficácia do algoritmo genético é claramente demonstrada ao comparar o fitness da primeira geração com o da última. Na geração inicial, as soluções são aleatórias, resultando em um fitness muito alto devido a rotas longas e altas penalidades por violação de restrições. Após o tempo de execução, o fitness da melhor solução encontrada é drasticamente menor. Isso indica que o algoritmo foi capaz de minimizar a distância total percorrida e, ao mesmo tempo, encontrar uma configuração de rotas que respeita a capacidade dos veículos e a prioridade das entregas.

## 7. Desafios Enfrentados e Próximos Passos

Ajustar o peso das penalidades na função fitness foi o maior desafio. Um valor de penalidade muito baixo faria o algoritmo ignorar as restrições, enquanto um valor muito alto poderia impedir a exploração de boas soluções que temporariamente violam uma restrição. Foi necessário um ajuste fino para encontrar um equilíbrio que guiasse a evolução de forma eficaz.

Como próximo passo, o projeto está pronto para a integração com LLMs para a geração de relatórios de rota, conforme o requisito original do desafio. Os dados detalhados de cada rota, já salvos em arquivos CSV, podem ser usados como contexto para que um LLM gere um sumário em linguagem natural para cada motorista, descrevendo sua rota, a ordem das entregas e informações importantes.

## Licença


Este projeto está licenciado sob a licença CC0 1.0 Universal. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
