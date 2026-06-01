# Proposta Inicial do Jogo

Este documento apresenta a proposta do jogo desenvolvido em Python e Pygame para a disciplina de Introdução a Algoritmos/Programação.

## 1. Nome provisório do jogo

> Street Fighter x King of Fighters

## 2. Integrantes do grupo

- Enzo Fernandes Alcântara
- miguel de freitas abood

## 3. Tipo de jogo

Tipo escolhido pelo grupo:

> Jogo de luta 2D local para dois jogadores.

## 4. Descrição geral do jogo

O jogo é uma luta 2D local para dois jogadores no mesmo teclado. Cada jogador controla um lutador que pode andar, pular e atacar o adversário até reduzir a vida do oponente a zero.

A tela exibe dois personagens em combate, barras de vida para cada um, e animações para movimento, salto e ataques.

## 5. Objetivo do jogador

O objetivo principal de cada jogador é derrotar o adversário reduzindo sua barra de vida a zero antes que a sua própria vida acabe.

## 6. Regras principais

- Cada jogador escolhe um lutador.
- Ambos tem uma barra de vida e uma barra de super.
- Ambos os personagens tem ataques leves, pesados, especiais e supers.
- O lutador deve permanecer dentro dos limites da tela.
- Golpes especiais podem ser executados com a combinação de direção e ataque.

## 7. Condição de vitória

O jogador vence quando o adversário fica com 0 pontos de vida. O confronto termina imediatamente quando uma das barras de vida se esgota.

## 8. Condição de derrota ou encerramento

A partida termina com derrota de um jogador quando sua vida chega a zero. Não há tempo limite na versão atual do jogo.

## 9. Elementos previstos no jogo

### Jogador ou elemento principal

Dois lutadores controláveis localmente pelo mesmo teclado. Cada lutador possui movimento horizontal, salto e ataques.

### Obstáculos, inimigos ou desafios

O desafio principal é o próprio adversário, que tenta atacar e reduzir a vida do jogador. O jogador deve usar deslocamento, salto e ataques estratégicos para evitar ser atingido.

### Itens, alvos ou objetos de interação

Não há itens coletáveis nesta proposta. A interação principal é o combate entre os dois lutadores.

### Pontuação, vidas, tempo ou progresso

Cada jogador tem uma barra de vida inicial de 1000 pontos. A partida não utiliza tempo; o progresso é determinado pela redução da vida do adversário.

## 10. Controles previstos

### Jogador 1

- `A`: andar para a esquerda
- `D`: andar para a direita
- `W`: pular
- `U`: ataque leve 1
- `I`: ataque leve 2
- `J`: ataque pesado 1
- `K`: ataque pesado 2

### Jogador 2

- `Seta esquerda`: andar para a esquerda
- `Seta direita`: andar para a direita
- `Seta para cima`: pular
- `Tecla 4 do teclado numérico`: ataque leve 1
- `Tecla 5 do teclado numérico`: ataque leve 2
- `Tecla 1 do teclado numérico`: ataque pesado 1
- `Tecla 2 do teclado numérico`: ataque pesado 2

## 11. Organização inicial do código

O projeto será organizado em módulos para manter a lógica separada da interface e dos dados:

- `main.py`: ponto de entrada e loop principal do jogo.
- `fighter.py`: classe do lutador, entradas, animações e ataques.
- `src/config.py`: constantes de configuração do jogo.
- `src/funcoes.py`: funções auxiliares para lógica de pontuação, colisões e limites.
- `src/sprites.py`: carregamento de sprites e imagens.
- `src/dados.py`: leitura e gravação de recorde.
- `tests/`: testes unitários para validar funções básicas.

- `main.py`: inicia o jogo;
- `src/jogo.py`: contém o loop principal;
- `src/config.py`: guarda configurações como tamanho da tela e cores;
- `src/funcoes.py`: contém funções auxiliares;
- `src/dados.py`: contém funções de leitura e escrita de arquivos.

Organização planejada:

> O código será mantido em módulos claros para separar responsabilidades. `main.py` inicia o jogo, `fighter.py` controla a lógica de cada personagem, `src/config.py` guarda constantes, `src/funcoes.py` cuida de lógica de colisão e pontuação, `src/sprites.py` carrega imagens e `src/dados.py` gerencia persistência de recorde.

## 12. Recursos externos previstos

Informe se o grupo pretende utilizar imagens, sons, fontes, tutoriais ou códigos externos.

Exemplo:

- imagens obtidas de banco gratuito;
- sons gratuitos;
- tutorial usado apenas como referência;
- fonte personalizada.

Recursos previstos:

- Imagens e sprites vindos do diretório `assets/`, que podem ser referências de jogos existentes.
- Tutorial e exemplos de Pygame para orientar a organização do código e o uso de eventos/colisões.
- Sem uso de bibliotecas externas além de `pygame` e `pytest`.

## 13. Principais dificuldades esperadas

Liste as dificuldades que o grupo acredita que poderá enfrentar.

Exemplos:

- movimentação do jogador;
- colisão entre objetos;
- controle de tempo;
- criação do ranking;
- organização do código;
- uso do GitHub;
- testes;
- exibição de textos na tela.

Dificuldades previstas:

- Ajustar a lógica de controle de dois jogadores no mesmo teclado sem conflito de teclas.
- Garantir que as colisões e os ataques sejam detectados corretamente.
- Manter a organização do código com módulos separados e claros.

## 14. Escopo mínimo para a entrega final

Descreva qual será a versão mínima aceitável do jogo.

Esta seção é importante para evitar que o grupo escolha uma ideia grande demais.

Exemplo:

> A versão mínima do jogo terá um personagem controlado pelo teclado, obstáculos aparecendo na tela, sistema de vidas, sistema de pontuação e tela de fim de jogo.

Escopo mínimo:

> A versão mínima terá dois lutadores controláveis localmente, movimento básico, salto, ataques leves, detecção de colisão entre personagens, barras de vida funcionais e fim de partida quando um dos jogadores perder toda a vida.

## 15. Possíveis melhorias, caso haja tempo

Liste funcionalidades extras que o grupo poderá implementar se conseguir concluir o escopo mínimo.

Exemplos:

- tela inicial;
- sons;
- fases;
- aumento de dificuldade;
- ranking;
- animações;
- novos tipos de obstáculos;
- diferentes personagens;
- menu de pausa.

Melhorias possíveis:

- Adicionar tela inicial e tela de vitória/derrota.
- Incluir sons para ataques, impactos e ambiente.
- Criar um segundo personagem com sprites diferentes ou outros golpes.
