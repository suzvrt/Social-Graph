"""Text shown in the Information dialog, kept apart from widget code so it is easy to edit."""

HOW_TO = [
    ("Importar um grafo",
     "Abra o menu 'Arquivo' na barra superior e selecione 'Importar'. O arquivo deve estar no formato '.txt'"
     " (veja 'Formato do arquivo' na aba 'Mais'). Os vértices são posicionados automaticamente para reduzir"
     " cruzamentos; depois é possível arrastá-los livremente."),
    ("Exportar um grafo",
     "Abra o menu 'Arquivo' e selecione 'Exportar'. Enquanto houver alterações não exportadas, o título da"
     " janela começa com '*', e o programa avisa antes de criar um novo grafo, importar outro ou fechar."),
    ("Adicionar um vértice",
     "Abra o menu 'Criar...', selecione 'Vértice' e insira o nome: apenas letras, sem espaços, com no máximo"
     " 10 caracteres. A primeira letra é colocada em maiúscula automaticamente."),
    ("Mover um vértice",
     "Clique com o botão esquerdo sobre o vértice e arraste. As arestas acompanham o movimento e desviam de"
     " outros vértices quando necessário."),
    ("Marcar vértices",
     "Segure Ctrl e clique com o botão esquerdo sobre um vértice. Até dois vértices ficam marcados: o primeiro,"
     " em verde, é a origem e o segundo, em roxo, é o destino. Marcar um terceiro desmarca o mais antigo."
     " Repita o Ctrl+clique sobre um vértice marcado para desmarcá-lo."),
    ("Adicionar uma aresta",
     "Com a origem e o destino marcados, abra o menu 'Criar...', selecione 'Aresta' e insira o peso"
     " (de 1 até 5; valores fora da faixa são ajustados)."),
    ("Alterar o peso de uma aresta",
     "Clique duas vezes sobre a aresta (ou sobre o seu peso) com o botão esquerdo, ou clique com o botão"
     " direito e escolha 'Alterar peso'."),
    ("Excluir uma aresta",
     "Clique com o botão direito sobre a aresta (ou sobre o seu peso) e escolha 'Excluir aresta'. Os vértices"
     " são mantidos."),
    ("Deletar um vértice",
     "Clique com o botão direito sobre o vértice e escolha 'Deletar'. A confirmação informa quantas arestas"
     " serão removidas junto com ele."),
]

ANALYSIS = [
    ("Menor caminho",
     "Marque a origem e o destino e clique em 'Menor caminho' na barra superior. O caminho de menor soma de"
     " pesos fica destacado por alguns segundos."),
    ("Recomendações",
     "Marque um único vértice e abra o menu 'Recomendações', ou clique com o botão direito sobre o vértice e"
     " escolha 'Recomendações'. Informe quantas sugestões deseja; empates com a última sugestão também são"
     " exibidos. O botão 'Adicionar' cria a aresta até a pessoa sugerida (peso limitado de 1 a 5)."),
    ("Por distância",
     "Sugere pessoas alcançáveis que o vértice ainda não segue, ordenadas pela distância do menor caminho."),
    ("Por distância ponderada",
     "Usa os mesmos candidatos, mas multiplica a distância por (total de arestas − número de seguidores do"
     " candidato). Assim, pessoas mais populares aparecem primeiro."),
    ("Leitura das arestas",
     "Cada seta vai de quem segue para quem é seguido, com o peso no meio. Arestas que passariam por cima de"
     " outro vértice são desenhadas curvas, e quando existem A → B e B → A as duas aparecem lado a lado."),
]

MORE = [
    ("Tema",
     "Abra o menu 'Exibir' e escolha 'Tema' para alternar entre o tema escuro e o claro. A escolha é lembrada"
     " na próxima vez que o programa for aberto."),
    ("Formato do arquivo",
     "Um comando por linha (linhas em branco são ignoradas):\n"
     "add <origem> <destino> <peso>   cria a aresta e os vértices que faltarem\n"
     "addv <nome>   cria um vértice isolado\n"
     "remove <nome>   remove um vértice e suas arestas\n"
     "Se uma linha for inválida, a importação é cancelada e o número da linha é informado."),
    ("Novidades da versão 2.0",
     "- Arestas desviam de vértices e arestas opostas não se sobrepõem;\n- Posicionamento automático ao"
     " importar;\n- Exclusão de arestas;\n- Aviso de alterações não salvas também ao apagar vértices e ao"
     " fechar;\n- Seleção de tema (escuro/claro);\n- Instruções de uso completas;\n- Código reorganizado,"
     " documentado e com testes."),
]

TABS = [
    ("Como usar", HOW_TO),
    ("Análise", ANALYSIS),
    ("Mais", MORE),
]

ABOUT = (
    "Software desenvolvido por Enzo Suzart Pinto, aluno do Polo Saquarema do curso de Tecnologia em Sistemas da"
    " Computação oferecido pela Fundação CECIERJ/Consórcio CEDERJ em função da 2ª Avaliação Distancial da"
    " disciplina Programação com Interfaces Gráficas no segundo semestre de 2019."
)
