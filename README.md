# street fighter x king of fighters

Projeto final da disciplina de Introdução a Algoritmos/Programação, desenvolvido em Python com Pygame.

Este repositório contém uma versão local de luta 2D para dois jogadores utilizando o mesmo teclado. O jogo apresenta dois lutadores controláveis, animações de movimento, salto, ataque leve e shoryuken, além de uma barra de vida para cada personagem.

## Integrantes do grupo

- Enzo Fernandes Alcântara
- miguel de freitas abood

## Estrutura do projeto

- `main.py`: ponto de entrada do jogo de luta.
- `fighter.py`: classe `Fighter` que controla movimento, ataques, animações e colisões.
- `src/`: módulos auxiliares do projeto.
  - `src/config.py`: constantes do jogo (tela, cores, FPS e caminhos).
  - `src/funcoes.py`: funções de lógica e utilitários.
  - `src/sprites.py`: carregamento e recorte de sprites.
  - `src/dados.py`: leitura e gravação de recorde.
  - `src/jogo.py`: versão adicional de loop de jogo com personagem, gema e inimigo.
- `assets/`: sprites, imagens de fundo, fontes e sons.
- `data/`: arquivos persistentes, como `recorde.txt`.
- `tests/`: testes unitários executáveis com `pytest`.
- `docs/`: documentação e proposta do projeto.

## Descrição do jogo

O jogo é uma luta 2D para dois jogadores em modo local. Cada jogador controla um lutador inspirado no estilo Street Fighter e deve atacar o oponente para reduzir sua barra de vida.

Os personagens podem andar, pular, recuar e executar ataques leves. Também há um golpe especial do tipo "shoryuken" que aplica mais dano quando executado corretamente.

## Objetivo do jogador

O objetivo é reduzir a vida do adversário a zero antes que o seu próprio lutador seja derrotado. O jogador que permanecer com vida vence a partida.

## Regras do jogo

- Cada lutador começa com 1000 de vida.
- Ataques bem-sucedidos reduzem 100 pontos de vida do adversário.
- A partida termina quando a vida de um dos lutadores chega a zero.
- O jogador deve manter o lutador dentro dos limites da tela.
- O golpe especial é ativado pela sequência de direção seguida da tecla de ataque apropriada.

## Controles

### Jogador 1

- `A`: andar para a esquerda
- `D`: andar para a direita
- `W`: pular
- `U`: ataque leve 1
- `I`: ataque leve 2
- `J`: ataque leve 3
- `K`: ataque leve 4
- `U` + sequência de direção `D`, `S`, `D`/`S` ou `F`: shoryuken leve/especial

### Jogador 2

- `Seta esquerda`: andar para a esquerda
- `Seta direita`: andar para a direita
- `Seta para cima`: pular
- `Tecla 4 do teclado numérico`: ataque leve 1
- `Tecla 5 do teclado numérico`: ataque leve 2
- `Tecla 1 do teclado numérico`: ataque leve 3
- `Tecla 2 do teclado numérico`: ataque leve 4
- `Tecla 4 do teclado numérico` + sequência de direção: shoryuken leve/especial

> Observação: as teclas de ataque do segundo jogador usam o teclado numérico (`KP4`, `KP5`, `KP1`, `KP2`).

## Como executar o projeto

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o jogo

```bash
python main.py
```

## Como executar os testes

```bash
python -m pytest
```

## Checklist mínimo para entrega

- [x] Preencher o README com nome final, descrição real, regras e controles do jogo.
- [ ] Atualizar `docs/proposta.MD` com a proposta do grupo.
- [x] Garantir que o jogo executa com `python main.py`.
- [x] Garantir que os testes passam com `pytest`.

## Observações

- Mantenha o código modular e bem comentado.
- Use `src/` para lógica adicional e mantenha o loop principal em `main.py`.
- Documente decisões importantes no `docs/proposta.MD`.
