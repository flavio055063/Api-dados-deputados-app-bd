# //////////////////////////////////////
# // ALUNO: FLÁVIO AUGUSTO ALÓ TORRES //
# // NUM. DE MATRÍCULA: 2020030477    //
# // TRABALHO PRATICO 01              //
# // BANCO DE DADOS 2                 //
# // DATA DE ENTREGA: 27/11/2021      //
# //////////////////////////////////////

# biblioteca para utilizar o metodo GET para pegar info da API
import requests

# biblioteca para abrir o arquivo json e converter XML para json
import json

# biblioteca que permite fazer o dataframe
import pandas as pd

# driver de conexão
import psycopg2

# bibliotecas necessárias para gerar os gráficos
import seaborn
import matplotlib.pyplot as plt

# biblioteca grafica tkinter
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import Deputado

class LimitePrincipal():
    def __init__(self, root, controle):
        self.controle = controle
        self.root = root
        self.root.geometry('500x400')
        self.menubar = tk.Menu(self.root)
        self.DeputadoMenu = tk.Menu(self.menubar)
        self.GastosMenu = tk.Menu(self.menubar)
        self.PopularBancoMenu = tk.Menu(self.menubar)

        #adicionando os comandos ao menu
        self.DeputadoMenu.add_command(label="Consulta por id", \
            command=self.controle.consultaDeputadoId)

        self.DeputadoMenu.add_command(label="Consulta por nome", \
            command=self.controle.consultaDeputadoNome)

        self.GastosMenu.add_command(label="Gasto por deputado", \
            command=self.controle.consultaGastoDeputado)
        
        self.GastosMenu.add_command(label="Gasto por partido", \
            command=self.controle.consultaGastoPartido)

        self.GastosMenu.add_command(label="Ver part. que mais gastam", \
            command=self.controle.verPartMaisGastam)

        self.PopularBancoMenu.add_command(label="Pop. BD (administrador)", \
            command=self.controle.popularBanco)

        #criando a cascade
        self.menubar.add_cascade(label="Consultar Deputado", \
            menu=self.DeputadoMenu)

        self.menubar.add_cascade(label="Consultar Gastos", \
            menu=self.GastosMenu)

        self.menubar.add_cascade(label="Popular banco de dados", \
            menu=self.PopularBancoMenu)

        self.root.config(menu=self.menubar)


class ControlePrincipal():
    def __init__(self):
        self.root = tk.Tk()
        self.ctrlDeputado = Deputado.CtrlDeputado(self)

        self.limite = LimitePrincipal(self.root, self)
        self.root.title("Sistema de Deputados")

        self.root.mainloop()

    def consultaDeputadoId(self):
      self.ctrlDeputado.consultaDeputadoId()

    def consultaDeputadoNome(self):
      self.ctrlDeputado.consultaDeputadoNome()

    def consultaGastoDeputado(self):
      self.ctrlDeputado.consultaGastoDeputado()

    def consultaGastoPartido(self):
      self.ctrlDeputado.consultaGastoPartido()

    def popularBanco(self):
      self.ctrlDeputado.popularBanco()

    def verPartMaisGastam(self):
      self.ctrlDeputado.verPartMaisGastam()

if __name__ == '__main__':
    c = ControlePrincipal()

