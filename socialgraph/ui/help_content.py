"""Text shown in the Information dialog, kept apart from widget code so it is easy to edit."""

HOW_TO = [
    ("Importar um grafo",
     "Abra o menu 'Arquivo' na barra superior, então selecione 'Importar'. O arquivo gerador deve estar no"
     " formato '.txt', com os comandos adequados. Atenção: os elementos são posicionados aleatoriamente sempre"
     " que importados. Certas arestas podem se sobrepor nesse processo, entretanto é possível movimentar"
     " vértices para melhor visualização."),
    ("Adicionar um vértice",
     "Abra o menu 'Criar...' na barra superior, selecione 'Vértice', então insira o nome (limite: 10"
     " caracteres)."),
    ("Marcar vértices",
     "Aperte a tecla Ctrl e então clique com o botão esquerdo em cima de um vértice. Apenas dois vértices podem"
     " ser selecionados por vez, o primeiro a ser selecionado, marcado em verde, será o vértice de partida e o"
     " seguinte, marcado em roxo, será o vértice de destino."),
    ("Adicionar uma aresta",
     "Com os dois vértices desejados marcados, abra o menu 'Criar...' na barra superior, selecione 'Aresta',"
     " então insira o peso desejado (de 1 até 5)."),
    ("Deletar um vértice",
     "Aperte com o botão direito no vértice desejado e então selecione 'Deletar' no menu."),
    ("Alterar o peso de uma aresta",
     "Clique duas vezes na aresta desejada com o botão esquerdo e então insira o novo peso."),
]

MORE = [
    ("Não implementado",
     "- Detecção de colisão de arestas;\n- Otimização estrutural do código;\n- Exclusão de arestas;"
     "\n- Aviso de alteração ao apagar vértices;\n- Certas instruções de uso;\n- Seleção de tema."),
]

ABOUT = (
    "Software desenvolvido por Enzo Suzart Pinto, aluno do Polo Saquarema do curso de Tecnologia em Sistemas da"
    " Computação oferecido pela Fundação CECIERJ/Consórcio CEDERJ em função da 2ª Avaliação Distancial da"
    " disciplina Programação com Interfaces Gráficas no segundo semestre de 2019."
)
