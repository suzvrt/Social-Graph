"""@package SocialGraph
Visual application for creating and manipulating social graphs
@author: Enzo Suzart Pinto
@date: 02/09/2019
"""

from SocialGraph import *
from DiGraph import *
# import sys
from threading import Timer
import os.path
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter import *
from random import randint


def center(obj):
    obj.update_idletasks()
    width = obj.winfo_width()
    height = obj.winfo_height()
    x = (obj.winfo_screenwidth() // 2) - (width // 2)
    y = (obj.winfo_screenheight() // 2) - (height // 2) - 50
    obj.geometry('{}x{}+{}+{}'.format(width, height, x, y))


# noinspection PyBroadException
class SocialGraphGUI(Tk):
    def __init__(self, master=None):
        Tk.__init__(self, master)
        self.dg = DiGraph()
        self.drawn = []
        self.title("SocialGraph")
        self.iconbitmap("icon.ico")

        self.sg = None

        self.exported = True

        self.geometry("%sx%s" % (self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2))

        self.canvas = Canvas(self, bg="#2b2b2b")
        self.canvas.pack(expand=True, fill="both")

        self.menu = Menu(self)
        self.archive = Menu(self.menu, tearoff=False)
        self.archive.add_command(label="Novo", command=self.newGraph)
        self.archive.add_command(label="Importar", command=self.importGraph)
        self.archive.add_command(label="Exportar", command=self.exportGraph)
        self.menu.add_cascade(label="Arquivo", menu=self.archive)
        self.add = Menu(self.menu, tearoff=False)
        self.add.add_command(label="Vértice", command=self.addNode)
        self.add.add_command(label="Aresta", command=self.connectNodes)
        self.menu.add_cascade(label="Criar...", menu=self.add)
        self.menu.add_command(label="Menor caminho", command=self.shortestPath)
        self.rec = Menu(self.menu, tearoff=False)
        self.rec.add_command(label="Por distância", command=lambda: self.recFriends("dist"))
        self.rec.add_command(label="Por distância ponderada", command=lambda: self.recFriends("weightedDist"))
        self.menu.add_cascade(label="Recomendações", menu=self.rec)
        self.menu.add_command(label="Informações", command=self.openInfo)

        self.configure(menu=self.menu)

    def recFriends(self, opt):
        if self.canvas.find_withtag("$2"):
            messagebox.showwarning("Atenção!", "Selecione apenas um vértice")
        if self.canvas.find_withtag("$1"):
            poi = self.canvas.itemcget(self.canvas.find_withtag("$1"), "tags").split("°")[0]
            topK = simpledialog.askinteger("Recomendações", "Insira o número de recomendações:")
            if topK is not None:
                RecommendationsPopup(self, poi, opt, topK)
        else:
            messagebox.showwarning("Atenção!", "Selecione um vértice para obter recomendações.")

    def generateNode(self, node):
        if node not in self.dg.vertices():
            self.dg.addVertex(node)
            maxtry = 0
            while len(self.drawn) < len(self.dg.vertices()):
                overlapping = False
                r = 35
                x = randint(r + 5, self.canvas.winfo_width() - r - 5)
                y = randint(r + 5, self.canvas.winfo_height() - r - 5)
                for j in range(len(self.drawn)):
                    dist = ((x - self.drawn[j].x) ** 2 + (y - self.drawn[j].y) ** 2) ** 0.5
                    if dist < r * 3 or self.canvas.find_overlapping(x - r, y + r, x + r, y - r):
                        overlapping = True
                if not overlapping:
                    self.drawn.append(Node(x, y, r, node, self.canvas, self.dg))
                    self.drawn[-1].drawNode(self)
                maxtry += 1
                if maxtry > 25000:
                    raise Exception("Quantidade de vértices acima do limite\npermitido pelo tamanho da janela.")

    def shortestPath(self):
        src = dst = None
        for item in self.canvas.find_all():
            if "$1" in self.canvas.itemcget(item, "tags"):
                src = self.canvas.itemcget(item, "tags").split(" ")[0].replace('°', '')
            if "$2" in self.canvas.itemcget(item, "tags"):
                dst = self.canvas.itemcget(item, "tags").split(" ")[0].replace('°', '')

        if src is not None and dst is not None:
            path = self.dg.Dijkstra2(src, dst)
            if path:
                for i in range(len(path) - 1):
                    self.canvas.itemconfig(path[i].getVertex() + '|' + path[i + 1].getVertex(), fill="#5c96ba")
                    self.canvas.itemconfig(path[i].getVertex() + '°', outline="#5c96ba")
                    self.canvas.itemconfig(path[i + 1].getVertex() + '°', outline="#5c96ba")
                t = Timer(4.0, lambda: self.defaultColor(path))
                t.start()
            else:
                messagebox.showwarning("Aviso!", "Não existe um caminho entre os dois vértices selecionados.")
        else:
            messagebox.showwarning("Atenção!", "Selecione dois vértices para mostrar o menor caminho.")

    def generateEdge(self, src, dst, cst):
        self.dg.addEdge(src, dst, cst)
        Connect(src, cst, dst, self.canvas).drawConnect(self)

    def connectNodes(self, src=None, dst=None, cst=None):
        if src is None and dst is None:
            for item in self.canvas.find_all():
                if "$1" in self.canvas.itemcget(item, "tags"):
                    src = self.canvas.itemcget(item, "tags").split(" ")[0].replace('°', '')
                if "$2" in self.canvas.itemcget(item, "tags"):
                    dst = self.canvas.itemcget(item, "tags").split(" ")[0].replace('°', '')

        if src is not None:
            if dst is not None:
                if not self.dg.hasEdge(src, dst):
                    if cst is None:
                        cst = simpledialog.askinteger("Nova aresta", "Insira o peso da aresta:")
                    if cst is not None:
                        if cst > 5:
                            cst = 5
                        elif cst < 1:
                            cst = 1
                        self.generateEdge(src, dst, cst)
                        self.exported = False
                else:
                    msg = "Já há uma aresta entre os dois pontos.\nCaso deseje alterar o peso, acesse 'Informações'\n"
                    msg += "para saber como."
                    messagebox.showwarning("Atenção!", msg)
            else:
                messagebox.showwarning("Atenção!", "Para criar uma aresta, selecione dois vértices.")
        else:
            messagebox.showwarning("Atenção!", "Para criar uma aresta, selecione dois vértices.")

    def importGraph(self, opt=0):
        if opt == 0 and not self.exported:
            a = ExportDialog(2, self)
            a.grab_set()
        else:
            filename = filedialog.askopenfilename(filetypes=[("Arquivos de texto (*.txt)", "*.txt")])
            if filename:
                try:
                    self.cleanGraph()
                    sg = SocialGraph(filename)

                    if str(sg.dg) == str(DiGraph()):
                        raise Exception("O arquivo não gera um grafo.")

                    self.title("%s - SocialGraph" % (filename.split("/", -1)[-1])[:-4])
                    self.sg = sg
                    for node in sg.dg.vertices():
                        self.generateNode(node)
                        if sg.dg.incomingEdges(node) != set():
                            for edge in sg.dg.incomingEdges(node):
                                if edge.getVertex() in self.dg.vertices():
                                    self.generateEdge(edge.getVertex(), node, edge.getCost())
                        if sg.dg.adjacentTo(node) != set():
                            for edge in sg.dg.adjacentTo(node):
                                if edge.getVertex() in self.dg.vertices():
                                    self.generateEdge(node, edge.getVertex(), edge.getCost())

                except Exception as e:
                    self.cleanGraph()
                    messagebox.showwarning("Erro!", e)

    def addNode(self):
        nodeName = simpledialog.askstring("Criar vértice", "Insira o nome:")
        if not nodeName:
            pass
        elif nodeName in self.dg.vertices():
            messagebox.showwarning("Atenção!", "O grafo já possui um vértice %s." % nodeName)
        elif not nodeName.isalpha():
            messagebox.showwarning("Atenção!", "Números e símbolos não permitidos.")
        else:
            self.generateNode(nodeName.capitalize())
            self.exported = False

    def exportGraph(self):
        if str(self.dg) != str(DiGraph()):
            filename = filedialog.asksaveasfilename(filetypes=[("Arquivos de texto (*.txt)", "*.txt")])
            if filename:
                if filename[-4:] != ".txt":
                    if not os.path.isfile(filename + ".txt"):
                        filename += ".txt"
                    else:
                        filename += " (1).txt"
                with open(filename, "w+") as f:
                    for edge in self.dg.edges():
                        s = "add " + edge[0] + " " + edge[2] + " " + str(edge[1]) + "\n"
                        f.writelines(s)

                    for vertice in self.dg.vertices():
                        if self.dg.adjacentTo(vertice) == set() and self.dg.incomingEdges(vertice) == set():
                            s = "addv " + vertice + "\n"
                            f.writelines(s)
                self.title("%s - SocialGraph" % (filename.split("/", -1)[-1])[:-4])
                self.exported = True
        else:
            messagebox.showwarning("Grafo vazio!", "O grafo atual está vazio.")

    def cleanGraph(self):
        self.dg = DiGraph()
        self.drawn = []
        self.canvas.delete("all")
        self.title("SocialGraph")

    def newGraph(self, opt=0):
        if opt == 0 and not self.exported:
            a = ExportDialog(1, self)
            a.grab_set()
            a.focus_set()
        elif self.canvas.find_all() != tuple():
            self.cleanGraph()

    def openInfo(self):
        a = InfoDialog(self)
        a.grab_set()
        a.focus_set()

    def defaultColor(self, obj):
        for i in range(len(obj) - 1):
            self.canvas.itemconfig(obj[i].getVertex() + '|' + obj[i + 1].getVertex(), fill="#ffc66d")
            if "$1" not in self.canvas.itemcget(obj[i].getVertex() + '°', "tags"):
                if "$2" not in self.canvas.itemcget(obj[i].getVertex() + '°', "tags"):
                    self.canvas.itemconfig(obj[i].getVertex() + '°', outline="#cc7832", fill="#2b2b2b")
                else:
                    self.canvas.itemconfig(obj[i].getVertex() + '°', fill="#2a2a5a", outline="#b200b2")
            else:
                self.canvas.itemconfig(obj[i].getVertex() + '°', fill="#3b514d", outline="#e0ee27")
        tagds = self.canvas.itemcget(obj[-1].getVertex() + '°', "tags")
        if "$1" not in tagds:
            if "$2" not in tagds:
                self.canvas.itemconfig(obj[-1].getVertex() + '°', outline="#cc7832", fill="#2b2b2b")
            else:
                self.canvas.itemconfig(obj[-1].getVertex() + '°', fill="#2a2a5a", outline="#b200b2")


class Node(Canvas):
    def __init__(self, x, y, r, n, canvas, dg):
        super(Node, self).__init__()
        self.x = x
        self.y = y
        self.r = r
        self.n = n[:10]
        self.canvas = canvas
        self.rightClick = Menu(self, tearoff=False)
        self.rightClick.add_command(label="Recomendações")
        self.rightClick.add_command(label="Deletar", command=lambda: self.deleteNode(dg))

    def drawNode(self, master):
        self.canvas.create_oval(self.x - self.r, self.y + self.r, self.x + self.r, self.y - self.r, fill="#2b2b2b",
                                width=1.5, tags=self.n + '°', outline="#cc7832")
        self.canvas.create_text(self.x, self.y, text=self.n, tags=self.n, fill="#a9b7c6", font=("Segoe UI", 9, "bold"))
        self.canvas.tag_bind(self.n, "<Button-3>", self.contextMenu)
        self.canvas.tag_bind(self.n + '°', "<Button-3>", self.contextMenu)
        self.canvas.tag_bind(self.n, "<B1-Motion>", lambda e: self.moveNode(e, master))
        self.canvas.tag_bind(self.n + '°', "<B1-Motion>", lambda e: self.moveNode(e, master))
        self.canvas.tag_bind(self.n, "<Control-1>", lambda e: self.selectNode())
        self.canvas.tag_bind(self.n + '°', "<Control-1>", lambda e: self.selectNode())

    def contextMenu(self, event):
        self.selectNode()
        self.rightClick.tk_popup(event.x_root, event.y_root, 0)

    def selectNode(self):
        if "$1" in self.canvas.itemcget(self.n + '°', "tags") or "$2" in self.canvas.itemcget(self.n + '°', "tags"):
            self.canvas.itemconfig(self.n + '°', tags=self.canvas.itemcget(self.n + '°', "tags").split(" ")[0],
                                   fill="#2b2b2b", outline="#cc7832")
            if self.canvas.find_withtag("$2"):
                self.canvas.itemconfig(self.canvas.find_withtag("$2")[0], tags=
                                       self.canvas.itemcget(self.canvas.find_withtag("$2")[0], "tags").split(" ")[0]
                                       + " $1", fill="#3b514d", outline="#e0ee27")
        else:
            select = "$1"
            if self.canvas.find_withtag("$1"):
                select = "$2"
            if self.canvas.find_withtag("$2"):
                self.canvas.itemconfig(self.canvas.find_withtag("$1")[0], tags=
                                       self.canvas.itemcget(self.canvas.find_withtag("$1")[0], "tags").split(" ")[0],
                                       fill="#2b2b2b", outline="#cc7832")
                self.canvas.itemconfig(self.canvas.find_withtag("$2")[0], tags=
                                       self.canvas.itemcget(self.canvas.find_withtag("$2")[0], "tags").split(" ")[0]
                                       + " $1", fill="#3b514d", outline="#e0ee27")
            self.canvas.addtag_withtag(select, self.n + '°')
            if select == "$1":
                self.canvas.itemconfig(self.n + '°', fill="#3b514d", outline="#e0ee27")
            else:
                self.canvas.itemconfig(self.n + '°', fill="#2a2a5a", outline="#b200b2")

    def moveNode(self, event, master):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if 0 <= x <= self.canvas.winfo_width() and 0 <= y <= self.canvas.winfo_height():
            self.canvas.move(self.n, x - self.x, y - self.y)
            self.canvas.move(self.n + '°', x - self.x, y - self.y)
            self.x, self.y = x, y
            canvasitems = self.canvas.find_all()
            for item in canvasitems:
                tag = self.canvas.itemcget(item, "tags")
                if not isinstance(tag, tuple) and '|' in tag:
                    src = tag.split('|', 1)[0]
                    dst = tag.split('|', 1)[-1]
                    if src == self.n or dst == self.n:
                        cst = self.canvas.itemcget(src + '@' + dst, "text")
                        self.canvas.delete(item)
                        self.canvas.delete(src + "@" + dst)
                        self.canvas.delete(src + "[" + dst)
                        Connect(src, cst, dst, self.canvas).drawConnect(master)

    def deleteNode(self, dg):
        if messagebox.askyesno("Deletar vértice", "Tem certeza que deseja deletar %s?" % self.n):
            dg.removeVertex(self.n)
            self.canvas.delete(self.n)
            self.canvas.delete(self.n + '°')
            items = self.canvas.find_all()
            for item in items:
                tag = self.canvas.itemcget(item, "tags")
                if not isinstance(tag, tuple) and '|' in tag:
                    src = tag.split('|', 1)[0]
                    dst = tag.split('|', 1)[-1]
                    if src == self.n or dst == self.n:
                        self.canvas.delete(item)
                        self.canvas.delete(src + "@" + dst)
                        self.canvas.delete(src + "[" + dst)


class Connect(Canvas):
    def __init__(self, src, cst, dst, canvas):
        super(Connect, self).__init__()
        self.src = src
        self.dst = dst
        self.cst = cst
        self.canvas = canvas

    def drawConnect(self, master):
        src = {"x": self.canvas.coords(self.src + '°')[0] + 35,
               "y": self.canvas.coords(self.src + '°')[1] + 35}

        dst = {"x": self.canvas.coords(self.dst + '°')[0] + 35,
               "y": self.canvas.coords(self.dst + '°')[1] + 35}

        m = ((dst['x'] - src['x']) ** 2 + (dst['y'] - src['y']) ** 2) ** 0.5

        ax = ((src['x'] + 35 * (dst['x'] - src['x']) / m) ** 2) ** 0.5
        ay = ((src['y'] + 35 * (dst['y'] - src['y']) / m) ** 2) ** 0.5
        bx = ((dst['x'] - 35 * (dst['x'] - src['x']) / m) ** 2) ** 0.5
        by = ((dst['y'] - 35 * (dst['y'] - src['y']) / m) ** 2) ** 0.5

        self.canvas.create_line(ax, ay, bx, by, width=1.5, fill="#ffc66d", tags=self.src + '|' + self.dst,
                                arrow=LAST, capstyle=ROUND)
        self.canvas.create_text((ax + bx) // 2, (ay + by) // 2, text=self.cst, justify=CENTER,
                                fill="#94558d", font=("Segoe UI", 9, "bold"), tags=self.src + '@' + self.dst)
        cbox = self.canvas.bbox(self.src + '@' + self.dst)
        self.canvas.create_oval(cbox[0] - 0.5, cbox[1], cbox[2], cbox[3], fill="#2b2b2b", width=0,
                                tags=self.src + '[' + self.dst)
        self.canvas.tag_lower(self.src + '@' + self.dst)
        self.canvas.tag_lower(self.src + '[' + self.dst)
        self.canvas.tag_lower(self.src + '|' + self.dst)
        self.canvas.tag_bind(self.src + '|' + self.dst, '<Double-Button-1>', lambda e: self.changeWeight(master))
        self.canvas.tag_bind(self.src + '[' + self.dst, '<Double-Button-1>', lambda e: self.changeWeight(master))
        self.canvas.tag_bind(self.src + '@' + self.dst, '<Double-Button-1>', lambda e: self.changeWeight(master))

    def changeWeight(self, master):
        cst = simpledialog.askinteger("Mudar peso", "Insira o novo peso:")
        if cst is not None:
            if cst > 5:
                cst = 5
            elif cst < 1:
                cst = 1
            master.dg.addEdge(self.src, self.dst, cst)
            self.canvas.itemconfig(self.src + '@' + self.dst, text=cst)
            master.exported = False


class ExportDialog(Toplevel):
    def __init__(self, f=None, master=None):
        Toplevel.__init__(self, master)
        self.geometry("230x100+%s+%s" % ((self.winfo_screenwidth() // 2 - 115), (self.winfo_screenheight() // 2 - 50)))
        self.resizable(0, 0)
        self.title("Atenção!")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        Label(self, text="Mudanças não salvas, deseja:").grid(row=1, column=1, columnspan=3, sticky=NS)
        ttk.Button(self, text="Exportar", command=lambda: self.opt1(master, f)).grid(row=2, column=1, sticky=SW)
        ttk.Button(self, text="Continuar", command=lambda: self.opt2(master, f)).grid(row=2, column=2)
        ttk.Button(self, text="Cancelar", command=self.opt3).grid(row=2, column=3, sticky=E)

    def opt1(self, master, f):
        master.exportGraph()
        master.exported = True
        self.opt2(master, f)

    def opt2(self, master, f):
        self.destroy()
        if f == 1:
            master.newGraph(1)
        if f == 2:
            master.importGraph(1)

    def opt3(self):
        self.destroy()


class RecommendationsPopup(Toplevel):
    def __init__(self, master=None, poi=None, opt=None, topK=None):
        Toplevel.__init__(self, master)
        self.title("Recomendações - SocialGraph")
        self.resizable(0, 0)
        center(self)
        recommended = SocialGraph.recommendFriends(master.sg, poi, opt, topK, master.dg)
        if recommended:
            for i in range(len(recommended) + 1):
                self.rowconfigure(i, weight=1)
            for i in range(3):
                self.columnconfigure(i, weight=1)
            Label(self, text="Nome", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=NSEW)
            Label(self, text="Peso", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky=NSEW)
            Label(self, text="Opção", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky=NSEW)
            a = []
            for i in range(len(recommended)):
                Label(self, text=recommended[i].getVertex()).grid(row=i + 1, column=0, sticky=NSEW)
                Label(self, text=recommended[i].getCost()).grid(row=i + 1, column=1, sticky=NSEW)
                button = ttk.Button(self, text="Adicionar")
                button.grid(row=i + 1, column=2, sticky=NSEW)
                dst = recommended[i].getVertex()
                cst = recommended[i].getCost()
                button.configure(command=lambda d=dst, c=cst: self.addFriend(master, poi, d, c))
                a.append(button)
        else:
            self.destroy()
            messagebox.showwarning("Aviso!", "Não há sugestões disponíveis.")

    @staticmethod
    def addFriend(master, src, dst, cst):
        print(src, dst, cst)
        if not master.dg.hasEdge(src, dst):
            master.generateEdge(src, dst, cst)
            master.exported = False
        else:
            messagebox.showwarning("Atenção!", "Aresta já adicionada.")


class InfoDialog(Toplevel):
    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        self.geometry("%sx%s" % (self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2))
        self.resizable(0, 0)
        self.iconbitmap("icon.ico")
        self.title("Informações - SocialGraph")
        center(self)

        ntb = ttk.Notebook(self)
        ntb.pack(expand=True, fill="both")

        manual = Frame(ntb, bd=3)
        ntb.add(manual, text="Como usar")
        Label(manual, text="(Clique no item desejado para expandí-lo.)", font=("Segoe UI", 9, "italic"),
              fg="dark gray").pack(anchor=NW)
        ttk.Button(self, text="Fechar", command=lambda: self.destroy()).pack(anchor=S)

        imp_h = Button(manual, text="○ Importar um grafo:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(imp_h), borderwidth=0)
        imp_h.pack(anchor=NW)
        self.imp_l = Label(manual, text="")
        self.imp_l.pack(anchor=NW)

        adv_h = Button(manual, text="○ Adicionar um vértice:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(adv_h), borderwidth=0)
        adv_h.pack(anchor=NW)
        self.adv_l = Label(manual, text="")
        self.adv_l.pack(anchor=NW)

        mkv_h = Button(manual, text="○ Marcar vértices:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(mkv_h), borderwidth=0)
        mkv_h.pack(anchor=NW)
        self.mkv_l = Label(manual, )
        self.mkv_l.pack(anchor=NW)

        ade_h = Button(manual, text="○ Adicionar uma aresta:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(ade_h), borderwidth=0)
        ade_h.pack(anchor=NW)
        self.ade_l = Label(manual, text="")
        self.ade_l.pack(anchor=NW)

        del_h = Button(manual, text="○ Deletar um vértice:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(del_h), borderwidth=0)
        del_h.pack(anchor=NW)
        self.del_l = Label(manual, text="")
        self.del_l.pack(anchor=NW)

        chn_h = Button(manual, text="○ Alterar o peso de uma aresta:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(chn_h), borderwidth=0)
        chn_h.pack(anchor=NW)
        self.chn_l = Label(manual, text="")
        self.chn_l.pack(anchor=NW)

        more = Frame(ntb, bd=3)
        ntb.add(more, text="Mais")
        Label(more, text="(Clique no item desejado para expandí-lo.)", font=("Segoe UI", 9, "italic"),
              fg="dark gray").pack(anchor=NW)
        tbi_h = Button(more, text="○ Não implementado:", font=("Segoe UI", 9, "bold"),
                       command=lambda: self.showText(tbi_h), borderwidth=0)
        tbi_h.pack(anchor=NW)
        self.tbi_l = Label(more, text="\n")
        self.tbi_l.pack(anchor=NW)
        Label(more, text="__________________________________").pack(anchor=S)
        Label(more, text="Sobre o projeto", font=("Segoe UI", 10, "bold")).pack(anchor=S)
        Label(more, text="Software desenvolvido por Enzo Suzart Pinto, aluno do Polo Saquarema do curso de "
                         "Tecnologia em Sistemas da Computação oferecido pela Fundação CECIERJ/Consórcio CEDERJ "
                         "em função da 2ª Avaliação Distancial da disciplina Programação com Interfaces Gráficas "
                         "no segundo semestre de 2019.", wraplength=self.winfo_screenwidth() // 2 - 30,
              justify=LEFT).pack(anchor=S)

    def showText(self, target):
        if target.cget('text') == "○ Importar um grafo:":
            if self.imp_l.cget('text') == "":
                self.imp_l.configure(
                    text="Abra o menu 'Arquivo' na barra superior, então selecione 'Importar'. O arquivo gerador"
                         " deve estar no formato '.txt', com os comandos adequados. Atenção: os elementos são"
                         " posicionados aleatoriamente sempre que importados. Certas arestas podem se sobrepor nesse"
                         " processo, entretanto é possível movimentar vértices para melhor visualização.\n",
                    wraplength=self.winfo_screenwidth() // 2 - 30, justify=LEFT)
                self.adv_l.configure(text="")
                self.mkv_l.configure(text="")
                self.ade_l.configure(text="")
                self.del_l.configure(text="")
                self.chn_l.configure(text="")
            else:
                self.imp_l.configure(text="")

        if target.cget('text') == "○ Adicionar um vértice:":
            if self.adv_l.cget('text') == "":
                self.adv_l.configure(
                    text="Abra o menu 'Criar...' na barra superior, selecione 'Vértice', então insira o nome (limite:"
                         " 10 caracteres).\n", wraplength=self.winfo_screenwidth() // 2, justify=LEFT)
                self.imp_l.configure(text="")
                self.mkv_l.configure(text="")
                self.ade_l.configure(text="")
                self.del_l.configure(text="")
                self.chn_l.configure(text="")
            else:
                self.adv_l.configure(text="")

        if target.cget('text') == "○ Marcar vértices:":
            if self.mkv_l.cget('text') == "":
                self.mkv_l.configure(
                    text="Aperte a tecla Ctrl e então clique com o botão esquerdo em cima de um vértice. Apenas dois"
                         " vértices podem ser selecionados por vez, o primeiro a ser selecionado, marcado em verde,"
                         " será o vértice de partida e o seguinte, marcado em roxo, será o vértice de destino.\n",
                    wraplength=self.winfo_screenwidth() // 2 - 30, justify=LEFT)
                self.adv_l.configure(text="")
                self.imp_l.configure(text="")
                self.ade_l.configure(text="")
                self.del_l.configure(text="")
                self.chn_l.configure(text="")
            else:
                self.mkv_l.configure(text="")

        if target.cget('text') == "○ Adicionar uma aresta:":
            if self.ade_l.cget('text') == "":
                self.ade_l.configure(
                    text="Com os dois vértices desejados marcados, abra o menu 'Criar...' na barra superior,"
                         " selecione 'Aresta', então insira o peso desejado (de 0 até 5).\n",
                    wraplength=self.winfo_screenwidth() // 2 - 30, justify=LEFT)
                self.adv_l.configure(text="")
                self.mkv_l.configure(text="")
                self.imp_l.configure(text="")
                self.del_l.configure(text="")
                self.chn_l.configure(text="")
            else:
                self.ade_l.configure(text="")

        if target.cget('text') == "○ Deletar um vértice:":
            if self.del_l.cget('text') == "":
                self.del_l.configure(
                    text="Aperte com o botão direito no vértice desejado e então selecione 'Deletar' no menu.\n",
                    wraplength=self.winfo_screenwidth() // 2 - 30, justify=LEFT)
                self.adv_l.configure(text="")
                self.mkv_l.configure(text="")
                self.ade_l.configure(text="")
                self.imp_l.configure(text="")
                self.chn_l.configure(text="")
            else:
                self.del_l.configure(text="")

        if target.cget('text') == "○ Alterar o peso de uma aresta:":
            if self.chn_l.cget('text') == "":
                self.chn_l.configure(
                    text="Clique duas vezes na aresta desejada com o botão esquerdo e então insira o novo peso.\n",
                    wraplength=self.winfo_screenwidth() // 2 - 30, justify=LEFT)
                self.adv_l.configure(text="")
                self.mkv_l.configure(text="")
                self.ade_l.configure(text="")
                self.imp_l.configure(text="")
                self.del_l.configure(text="")
            else:
                self.chn_l.configure(text="")

        if target.cget('text') == "○ Não implementado:":
            if self.tbi_l.cget('text') == "\n":
                self.tbi_l.configure(
                    text="- Detecção de colisão de arestas;\n- Otimização estrutural do código;\n- Exclusão de arestas;"
                         "\n- Aviso de alteração ao apagar vértices;\n- Certas instruções de uso;\n- Seleção de tema.",
                    wraplength=self.winfo_screenwidth() // 2 - 30, justify=LEFT
                )
            else:
                self.tbi_l.configure(text="\n")


def main():
    app = SocialGraphGUI()
    center(app)
    app.mainloop()


if __name__ == '__main__':
    main()
