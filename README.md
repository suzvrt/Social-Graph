# SocialGraph

Editor visual de grafos sociais dirigidos e ponderados, feito em Python com Tkinter.

## Como executar

Requer Python 3.8+ (sem dependências externas).

```powershell
python -m socialgraph
```

O antigo `python SocialGraphGUI.py` continua funcionando.

Testes da camada de modelo:

```powershell
python -m unittest discover tests
```

## Funcionalidades

- Criar, mover e deletar vértices; criar, alterar o peso e excluir arestas.
- Importar/exportar grafos em `.txt`, com aviso de alterações não salvas.
- Menor caminho (Dijkstra) e recomendações de amizade por distância ou distância ponderada.
- Posicionamento automático ao importar; arestas desviam de vértices e arestas opostas não se sobrepõem.
- Temas escuro e claro (menu `Exibir > Tema`), lembrados entre execuções em `~/.socialgraph.json`.
- Instruções completas no menu `Informações`.

## Formato de arquivo

Arquivos `.txt` com um comando por linha:

```
add <origem> <destino> <peso>   # cria a aresta origem -> destino (e os vértices)
addv <nome>                     # cria um vértice isolado
remove <nome>                   # remove um vértice e suas arestas
```

Veja [infile.txt](infile.txt) como exemplo.

## Estrutura

```
socialgraph/
  config.py        constantes (raio do vértice, faixa de pesos, roteamento, caminhos)
  theme.py         paletas de cores
  settings.py      preferências do usuário
  model/           grafo, recomendações, nomes e leitura/escrita de arquivos (sem Tkinter)
  ui/              janela principal, canvas, geometria, diálogos e textos de ajuda
tests/             testes unitários (unittest)
```

## Sobre

Software desenvolvido por **Enzo Suzart Pinto**, aluno do Polo Saquarema do curso de Tecnologia em Sistemas da Computação oferecido pela Fundação CECIERJ/Consórcio CEDERJ em função da 2ª Avaliação Distancial da disciplina Programação com Interfaces Gráficas no segundo semestre de 2019.
