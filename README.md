# SocialGraph

Editor visual de grafos sociais dirigidos e ponderados, feito em Python com Tkinter.

## Como executar

Requer Python 3.8+ (sem dependências externas).

```powershell
python -m socialgraph
```

O antigo `python SocialGraphGUI.py` continua funcionando.

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
  config.py        constantes (raio do vértice, faixa de pesos, caminhos)
  theme.py         paletas de cores
  model/           grafo, recomendações e leitura/escrita de arquivos (sem Tkinter)
  ui/              janela principal, canvas, diálogos e textos de ajuda
```

## Sobre

Software desenvolvido por **Enzo Suzart Pinto**, aluno do Polo Saquarema do curso de Tecnologia em Sistemas da Computação oferecido pela Fundação CECIERJ/Consórcio CEDERJ em função da 2ª Avaliação Distancial da disciplina Programação com Interfaces Gráficas no segundo semestre de 2019.
