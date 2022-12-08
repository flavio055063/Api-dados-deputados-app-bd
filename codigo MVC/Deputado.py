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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# biblioteca grafica Tkinter
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# biblioteca para saber o diretório onde o código .py está
# rodando, para que possamos colocar os arquivos .json nesse diretorio
import os

#variavel para conexao e autenticação do usuario no banco de dados
# (por padrão qualquer usuario pode consultar os dados)
postgres_usuario = 'usuario_consulta'
postgres_senha = '159753'

#função de conexão do BD, com autenticação
def conecta_db():
  con = psycopg2.connect(host='localhost', database='db_deputados', user=postgres_usuario, password=postgres_senha)
  return con

#função para fazer uma inserção genérica no BD
def inserir_db(sql):
    con = conecta_db()
    cur = con.cursor()
    try:
        cur.execute(sql)
        con.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        con.rollback()
        cur.close()
        return 1
    cur.close()

#função para fazer uma consulta genérica no BD
def consultar_db(sql):
  con = conecta_db()
  cur = con.cursor()
  #executando consulta
  cur.execute(sql)
  #recebendo atraves do fetchall os dados
  dado_bruto = cur.fetchall()
  tuplas = []
  for i in dado_bruto:
    tuplas.append(i)
  con.close()
  return tuplas

#função que pega na API os detalhes do deputado
def detalhe_deputado(id):
  url        = 'https://dadosabertos.camara.leg.br/api/v2/deputados/' + id
  parametros = {}
  resposta   = requests.request("GET", url, params=parametros, timeout=7)
  objetos    = json.loads(resposta.text)
  #print(objetos)
  dados_ultimoStatus = objetos['dados']['ultimoStatus']
  dados_sexo = objetos['dados']['sexo']
  dados_redeSocial = objetos['dados']['redeSocial']
  dados_dataNascimento = objetos['dados']['dataNascimento']
  dados_escolaridade = objetos['dados']['escolaridade']
  dados_cpf = objetos['dados']['cpf']
  #df = pd.DataFrame(dados)
  #df.head()
  #df.info()
  return (dados_ultimoStatus, dados_sexo, dados_redeSocial, dados_dataNascimento, dados_escolaridade, dados_cpf)

# Função que pega os DISCURSOS dos deputados
def discurso_deputado(id):
  url        = 'https://dadosabertos.camara.leg.br/api/v2/deputados/' + id + '/discursos'
  parametros = {}
  resposta   = requests.request("GET", url, params=parametros, timeout=7)
  objetos_discurso    = json.loads(resposta.text)
  #print(objetos_discurso)
  dados_discurso = objetos_discurso['dados']

  df_discurso = pd.DataFrame(dados_discurso)
  #df.info()
  return (df_discurso)


class Deputado():
  def __init__(self):
    pass


class CtrlDeputado():
  def __init__(self, controlePrincipal):
    self.ctrlPrincipal = controlePrincipal
  
  # ---- criação das views ----- #
  def consultaDeputadoId(self):
    self.limiteConsId = LimiteconsultaDeputadoId(self)

  def consultaDeputadoNome(self):
    self.limiteConsNome = LimiteconsultaDeputadoNomes(self)

  def consultaGastoDeputado(self):
    self.limiteConsGastoDep = LimiteconsultaGastoDeputado(self)

  def consultaGastoPartido(self):
    self.limiteConsGastoPart = LimiteconsultaGastoPartido(self)
  
  def verPartMaisGastam(self):
    self.limiteVerPartMaisGastam = LimiteverPartMaisGastam(self)
    
  def popularBanco(self):
    self.limitePopularBanco = LimitepopularBanco(self)


  #função que retorna todos nomes de deputados (útil para a combobox)
  def getNomesDeputados(self):

    sql = ''' SELECT nome FROM deputados; '''
    nomes = []
    df_nomesDeputados = pd.DataFrame(consultar_db(sql), columns=['nome'])
    for i in range(len(df_nomesDeputados)):
      nomes.append(df_nomesDeputados['nome'][i])
    
    return(nomes)

  #função que retorna todas silgas de partido (útil para a combobox)
  def getSiglasPartidos(self):
    sql = ''' SELECT DISTINCT sigla FROM partidos; '''
    siglas = []
    df_siglas = pd.DataFrame(consultar_db(sql), columns=['sigla'])
    for i in range(len(df_siglas)):
      siglas.append(df_siglas['sigla'][i])
    
    return(siglas)

  #função que retorna os distintos anos na tabela gastos do BD
  def getAnosGastos(self):
    sql = ''' SELECT DISTINCT ano FROM gastos; '''
    anos = []
    df_anosGastos = pd.DataFrame(consultar_db(sql), columns=['ano'])
    for i in range(len(df_anosGastos)):
      anos.append(df_anosGastos['ano'][i])

    return(anos)

  #pega info basica de todos os deputados atuais
  def popularDeputados(self, event):

    global postgres_usuario
    postgres_usuario = str(self.limitePopularBanco.inputNome.get())
    global postgres_senha 
    postgres_senha = self.limitePopularBanco.inputSenha.get()

    print(postgres_usuario)
    print(postgres_senha)
    
    # Requisição dos dados dos Deputados
    url = 'https://dadosabertos.camara.leg.br/api/v2/deputados'
    parametros = {}
    resposta = requests.request("GET", url, params=parametros, timeout=7)
    objetos = resposta.json()
    #print(objetos)
    dados = objetos['dados']
    #print(dados)
    df = pd.DataFrame(dados)
    #df.info()

    #tratando os dados
    for col in df.columns:
      df[col] = df[col].apply(str)
    
    # Inserindo cada registro de DEPUTADO do DataFrame no BD
    for i in df.index:
        sql = """
        INSERT into public.deputados (id,uri,nome,siglaPartido,uriPartido,siglaUf,idLegislatura,urlFoto,email) 
        values('%s','%s','%s','%s','%s','%s','%s','%s','%s');
        """ % (df['id'][i], df['uri'][i], df['nome'][i], df['siglaPartido'][i], df['uriPartido'][i], df['siglaUf'][i], df['idLegislatura'][i], df['urlFoto'][i], df['email'][i])
        inserir_db(sql)

    return

  #preenche os dados adicionais de cada deputado na tabela deputados
  def popularDetalhesDeputados(self, event):

    global postgres_usuario
    postgres_usuario = str(self.limitePopularBanco.inputNome.get())
    global postgres_senha 
    postgres_senha = str(self.limitePopularBanco.inputSenha.get())

    print(postgres_usuario)
    print(postgres_senha)

    sql = ''' SELECT id FROM deputados; '''
    df_id = pd.DataFrame(consultar_db(sql), columns=['id'])
    for i in df_id.index:
    
      dados_ultimoStatus, dados_sexo, dados_redeSocial, dados_dataNascimento, dados_escolaridade, dados_cpf = detalhe_deputado(str(df_id['id'][i]))

      #criando dataframe para o ultimoStatus que veio da API
      df_ultimoStatus = pd.DataFrame(dados_ultimoStatus)
      #df_ultimoStatus.info() #descomentar para ver a estrutura gerada pelo pandas
      
      #tratando o dado do ultimoStatus
      for col in df_ultimoStatus.columns:
          df_ultimoStatus[col] = df_ultimoStatus[col].apply(str)

      #criando o SQL do UPDATE, inserindo as informações adicionais de cada deputado
      sql = """
      UPDATE public.deputados SET situacao = '%s', condicaoEleitoral = '%s', sexo = '%s', data_nasc = '%s', escolaridade = '%s', cpf = '%s', gabinete = ROW('%s', '%s', '%s', '%s', '%s', '%s') WHERE deputados.id = %s;
      """ % (df_ultimoStatus['situacao'][0], df_ultimoStatus['condicaoEleitoral'][0], dados_sexo, dados_dataNascimento, dados_escolaridade, dados_cpf, df_ultimoStatus['gabinete']['nome'], df_ultimoStatus['gabinete']['predio'], df_ultimoStatus['gabinete']['sala'], df_ultimoStatus['gabinete']['andar'], df_ultimoStatus['gabinete']['telefone'], df_ultimoStatus['gabinete']['email'],  df_ultimoStatus['id'][0])
      inserir_db(sql)

      #inserindo dados referentes a rede social desse candidato
      for j in range(len(dados_redeSocial)):
          sql = """INSERT into public.dep_redes_social VALUES ('%s', '%s'); """ % (df_ultimoStatus['id'][0], dados_redeSocial[j])
          inserir_db(sql)
    
    return

  #preenche a tabela dos discursos a partir de cada deputado
  def popularDiscursos(self, event):

    global postgres_usuario
    postgres_usuario = str(self.limitePopularBanco.inputNome.get())
    global postgres_senha 
    postgres_senha = str(self.limitePopularBanco.inputSenha.get())

    print(postgres_usuario)
    print(postgres_senha)

    sql = ''' SELECT id FROM deputados; '''
    df_id = pd.DataFrame(consultar_db(sql), columns=['id'])
    for i in df_id.index:
      df_discurso = discurso_deputado(str(df_id['id'][i]))
      for j in range(len(df_discurso)):
        sql = """
            INSERT into public.dep_discursos (dep_id, dataHoraInicio, tipoDiscurso, keywords, sumario, transcricao) 
            values('%s','%s','%s','%s','%s','%s');
            """ % (str(df_id['id'][i]), df_discurso['dataHoraInicio'][j], df_discurso['tipoDiscurso'][j], df_discurso['keywords'][j], df_discurso['sumario'][j], df_discurso['transcricao'][j])
        inserir_db(sql)

  #função para popular a tabela de partidos a partir dos partidos presentes na tabela deputado
  def popularPartidos(self, event):

    global postgres_usuario
    postgres_usuario = str(self.limitePopularBanco.inputNome.get())
    global postgres_senha 
    postgres_senha = str(self.limitePopularBanco.inputSenha.get())

    print(postgres_usuario)
    print(postgres_senha)

    # Pegando informações sobre o PARTIDO de cada deputado
    sql = """ SELECT DISTINCT uripartido FROM deputados; """
    df_links_partidos = pd.DataFrame(consultar_db(sql), columns=['uripartido'])

    #tratando os dados
    for col in df_links_partidos.columns:
        df_links_partidos[col] = df_links_partidos[col].apply(str)

    for i in df_links_partidos.index:
        # fazendo a requisição na API a partir dos links de cada partido
        url = df_links_partidos['uripartido'][i]
        parametros = {}
        # utilizando método GET para obter o arquivo xml
        resposta   = requests.request("GET", url, params=parametros, timeout=7)
        # transformando em json
        objetos_partidos = resposta.json()
        dados_partidos = objetos_partidos['dados']
        df_partidos = pd.DataFrame(dados_partidos)
        # montando o SQL de inserção. Percebi que o partido tem um líder que é necessariamente um deputado.
        # O json de resposta dos detalhes do partido (usando identificador dele) contém o URL que leva aos
        # detalhes do lider. Para facilitar, utilizei um fatiamento de string e obti do proprio link o
        # identificador (id) do deputado para usar como chave estrangeira. 
        sql = """
                INSERT into public.partidos (id_partido, sigla, nome, uripartido, id_lider) values('%s','%s','%s','%s','%s'); """ \
                % (df_partidos['id'][0], df_partidos['sigla'][0], df_partidos['nome'][0], df_partidos['uri'][0], int(df_partidos['status']['lider']['uri'][52:]))
        inserir_db(sql)

  #popula a tabela gastos a partir do .json obtido em (mais de 160k de tuplas):
  #https://dadosabertos.camara.leg.br/swagger/api.html#staticfile
  def popularGastos(self, event):
    
    global postgres_usuario
    postgres_usuario = str(self.limitePopularBanco.inputNome.get())
    global postgres_senha 
    postgres_senha = str(self.limitePopularBanco.inputSenha.get())

    print(postgres_usuario)
    print(postgres_senha)

    # Abrindo em formato de arquivo os gastos, porque a API está com algum problema
    # essa operação está demorando muito. O correto é inserir essas tuplas de outra maneira,
    # creio que há perda de tempo ao estabelecer conexões e finalizar conexões, além de ter que
    # inserir tupla por tupla...
    
    arquivos = []
    arquivos.append('gastos2022.json')
    arquivos.append('gastos2021.json')
    #mostra no terminal onde vc deve colocar o arquivo .json
    print(os.getcwd())

    for i in range(len(arquivos)):
      with open(arquivos[i], encoding='utf-8') as gastos_json:
          objetos_gastos = json.load(gastos_json)

      dados_gastos = objetos_gastos['dados']

      df_gastos = pd.DataFrame(dados_gastos)
      # df_gastos.info()
      # como existem gastos que nao pertencem a um deputado, e sim a liderança, excluirei os
      # dados que nao possuirem idDeputado... o dataframe identificou o idDeputado como float,
      # entao terei que converter para int.
      df_gastos['idDeputado'] = pd.to_numeric(df_gastos['idDeputado'], errors='coerce')
      df_gastos = df_gastos.dropna(subset=['idDeputado'])
      df_gastos['idDeputado'] = df_gastos['idDeputado'].apply(int)
      df_gastos['valorLiquido'] = df_gastos['valorLiquido'].apply(float)
      
      #tratando os dados (removendo aspas)
      #nesse caso poderia ser substituido por duas aspas ('') (in SQL you escape ' by adding an extra ') - de acordo stackoverflow
      for col in df_gastos.columns:
        df_gastos[col] = df_gastos[col].apply(str)

      for i, col in enumerate(df_gastos.columns):
        df_gastos.iloc[:, i] = df_gastos.iloc[:, i].str.replace("'", '')

      #abrindo conexao com o bd (nao usei a função pq estabelecer uma conexao toda hora demora muito para inserir multiplas tuplas)
      con = conecta_db()
      cur = con.cursor()

      #inserindo os dados relevantes de gastos do dataframe no PostgreSQL
      for i in df_gastos.index:
        sql = """
                  INSERT into public.gastos (id_deputado, legislatura, descricao, fornecedor, cnpjCPF, valorLiquido, mes, ano, url_documento) 
                  values('%s','%s','%s','%s','%s','%s', '%s', '%s', '%s');
                  """ % (df_gastos['idDeputado'][i], df_gastos['legislatura'][i], df_gastos['descricao'][i], df_gastos['fornecedor'][i], df_gastos['cnpjCPF'][i], df_gastos['valorLiquido'][i], df_gastos['mes'][i], df_gastos['ano'][i], df_gastos['urlDocumento'][i])
        try:
          cur.execute(sql)
          con.commit()
        except (Exception, psycopg2.DatabaseError) as error:
          print("Error: %s" % error)
          con.rollback()
      
      con.close()
        
  #função chamada quando o botao de consulta por id é clicado
  def consultaIdHandler(self, event):

    #lendo o dado inserido pelo usuario
    codigo = self.limiteConsId.inputCodigo.get()
  
    # criando o SQL de consulta do deputado
    sql = """ SELECT * FROM deputados WHERE id = '%s'; """ \
    % (int(codigo))
  
    df_consultaDeputadoId = pd.DataFrame(consultar_db(sql), columns=['id', 'uri', 'nome', 'siglaPartido', 'uriPartido', 'siglaUf', 'idLegislatura', 'urlFoto', 'email', 'gabinete', 'situacao', 'condicaoEleitoral', 'cpf', 'sexo', 'data_nasc', 'escolaridade'])
    # df_consultaDeputadoId.info() 
    # Desencapsulando e tratando os dados do gabinete, tirando o
    # parenteses e separando os itens pela virgula
    gabinete = df_consultaDeputadoId['gabinete'][0].replace('(', '').replace(')', '').split(',')
    
    imprime = 'id: ' + str(df_consultaDeputadoId['id'][0]) + '\nNome: ' + df_consultaDeputadoId['nome'][0] + '\nPartido: ' + df_consultaDeputadoId['siglaPartido'][0] + '\nEstado: ' + df_consultaDeputadoId['siglaUf'][0] + '\nLegislatura: ' + str(df_consultaDeputadoId['idLegislatura'][0]) + '\nGabinete: \n    Nome: ' + gabinete[0] + '\n    Predio: ' + gabinete[1]  + '\n    Sala: ' + gabinete[2] + '\n    Andar: ' + gabinete[3] + '\n    Telefone: ' + gabinete[4] + '\n    Email: ' + gabinete[5] + '\nEscolaridade: ' +  df_consultaDeputadoId['escolaridade'][0]
    self.limiteConsId.mostraJanela('Busca realizada', imprime)

  #função para limpar os campos de input
  def clearHandler(self, event):
    self.limiteConsId.inputCodigo.delete(0, len(self.limiteConsId.inputCodigo.get()))

  #função chamada quando o botao de consulta por nome é clicado
  def consultaNomeHandler(self, event):

    #lendo dado inserido pelo usuario
    nome = str(self.limiteConsNome.inputNome.get())
    nome = '%' + nome + '%'
  
    # criando o SQL de consulta por nome do deputado 
    sql = """ SELECT * FROM deputados WHERE nome ILIKE '%s' LIMIT 1; """ % (nome)

    #consultando o banco de dados e tratando os dados
    df_consultaDeputadoNome = pd.DataFrame(consultar_db(sql), columns=['id', 'uri', 'nome', 'siglaPartido', 'uriPartido', 'siglaUf', 'idLegislatura', 'urlFoto', 'email', 'gabinete', 'situacao', 'condicaoEleitoral', 'cpf', 'sexo', 'data_nasc', 'escolaridade'])
    gabinete = df_consultaDeputadoNome['gabinete'][0].replace('(', '').replace(')', '').split(',')
    imprime = 'id: ' + str(df_consultaDeputadoNome['id'][0]) + '\nNome: ' + df_consultaDeputadoNome['nome'][0] + '\nPartido: ' + df_consultaDeputadoNome['siglaPartido'][0] + '\nEstado: ' + df_consultaDeputadoNome['siglaUf'][0] + '\nLegislatura: ' + str(df_consultaDeputadoNome['idLegislatura'][0]) + '\nGabinete: \n    Nome: ' + gabinete[0] + '\n    Predio: ' + gabinete[1]  + '\n    Sala: ' + gabinete[2] + '\n    Andar: ' + gabinete[3] + '\n    Telefone: ' + gabinete[4] + '\n    Email: ' + gabinete[5] + '\nEscolaridade: ' +  df_consultaDeputadoNome['escolaridade'][0]
    messagebox.showinfo('Busca realizada', imprime)

  #função chamada quando o botao de consulta na janela de gasto por dep. é clicado
  def consultaGastoDeputadoHandler(self, event):
      nome = self.limiteConsGastoDep.escolhaComboNome.get()
      ano = self.limiteConsGastoDep.escolhaComboAno.get()

      sql = ''' SELECT sum(valorliquido), mes FROM gastos WHERE id_deputado = (SELECT id FROM deputados WHERE nome = '%s' LIMIT 1) and ano = %s GROUP BY mes ORDER BY mes; ''' \
        % (nome, ano)
      
      df_gastos = pd.DataFrame(consultar_db(sql),  columns=['valor', 'mes'])
      figure = plt.Figure(figsize=(8,6), dpi=100)

      y = df_gastos['valor'].apply(float)
      x = df_gastos['mes'].apply(int)
      
      ax = figure.add_subplot(111)
      ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
      ax.ticklabel_format(style='plain')
      chart_type = FigureCanvasTkAgg(figure, self.limiteConsGastoDep)
      chart_type.get_tk_widget().pack()
      ax.set_title('Gasto do deputado escolhido')

  #função chamada quando o botao de consulta na janela de gasto por partido é clicado
  def consultaGastoPartidoHandler(self,event):

      partido = self.limiteConsGastoPart.escolhaComboPartido.get()
      ano = self.limiteConsGastoPart.escolhaComboAno.get()

      sql = ''' SELECT gas.mes, sum(gas.valorliquido) FROM deputados dep, gastos gas WHERE gas.id_deputado = dep.id AND
       gas.ano = %s AND dep.siglapartido = '%s' GROUP BY gas.mes ORDER BY gas.mes; ''' \
        % (ano, partido)
      
      df_gastos = pd.DataFrame(consultar_db(sql),  columns=['mes', 'valor'])
      figure = plt.Figure(figsize=(8,6), dpi=100)

      y = df_gastos['valor'].apply(float)
      x = df_gastos['mes'].apply(int)
      
      ax = figure.add_subplot(111)
      ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
      ax.ticklabel_format(style='plain')
      chart_type = FigureCanvasTkAgg(figure, self.limiteConsGastoPart)
      chart_type.get_tk_widget().pack()
      ax.set_title('Gasto do partido escolhido')

#view da consulta dos deputados por ID
class LimiteconsultaDeputadoId(tk.Toplevel):
  def __init__(self, controle):
    tk.Toplevel.__init__(self)
    self.geometry('300x100')
    self.title("Obtenha inf. do deputado")
    self.controle = controle
    
    #crição dos frames
    self.frameCodigo = tk.Frame(self)
    self.frameButton = tk.Frame(self)

    self.frameCodigo.pack()
    self.frameButton.pack()

    #colocando as labels nas linhas (frames)
    self.labelCodigo = tk.Label(self.frameCodigo, text="id: ")

    self.labelCodigo.pack(side="left")

    #criando os campos de input
    self.inputCodigo = tk.Entry(self.frameCodigo, width=20)

    self.inputCodigo.pack()

    #criação dos botões
    self.buttonSubmit = tk.Button(self.frameButton ,text="Buscar")
    self.buttonSubmit.pack(side="left")
    self.buttonSubmit.bind("<Button>", controle.consultaIdHandler)

    self.buttonClear = tk.Button(self.frameButton,text="Limpar")
    self.buttonClear.pack(side="left")
    self.buttonClear.bind("<Button>", controle.clearHandler)

  def mostraJanela(self, titulo, msg):
        messagebox.showinfo(titulo, msg)

#view da consulta dos deputados por Nome
class LimiteconsultaDeputadoNomes(tk.Toplevel):
  def __init__(self, controle):
      tk.Toplevel.__init__(self)
      self.geometry('300x125')
      self.title("Consulta Deputados por nome")
      self.controle = controle

      #criação dos frames
      self.frameNome = tk.Frame(self)
      self.frameNome.pack()
      self.frameButton = tk.Frame(self)
      self.frameButton.pack()

      #criação das labels
      self.labelNome = tk.Label(self.frameNome, text="Nome: ")
      self.labelNome.pack(side="left")

      #criando os campos de input
      self.inputNome = tk.Entry(self.frameNome, width=20)
      self.inputNome.pack()

      self.buttonSubmit = tk.Button(self.frameButton ,text="Consultar")
      self.buttonSubmit.pack(side="left")
      self.buttonSubmit.bind("<Button>", controle.consultaNomeHandler)

#view da consulta dos gastos dos deputados
class LimiteconsultaGastoDeputado(tk.Toplevel):
  def __init__(self, controle):
      tk.Toplevel.__init__(self)
      self.geometry('1100x750')
      self.title("Consulta Gasto por Deputado")
      self.controle = controle

      #criação dos frames
      self.frameComboNome = tk.Frame(self)
      self.frameComboAno = tk.Frame(self)
      
      self.frameComboNome.pack()
      self.frameComboAno.pack()

      self.frameButton = tk.Frame(self)
      self.frameButton.pack()

      #criação das labels
      self.labelComboNome = tk.Label(self.frameComboNome, text="Nome: ")
      self.labelComboNome.pack(side="left")

      self.labelComboAno = tk.Label(self.frameComboAno, text="Ano: ")
      self.labelComboAno.pack(side="left")

      #criação das comboboxes
      self.escolhaComboNome = tk.StringVar()
      self.comboboxNome = ttk.Combobox(self.frameComboNome, width = 15, textvariable = self.escolhaComboNome)
      self.comboboxNome.pack(side="left")
      self.comboboxNome['values'] = controle.getNomesDeputados()
      self.escolhaComboNome.set("")

      #configuracao das comboboxes
      self.escolhaComboAno = tk.StringVar()
      self.comboboxAno = ttk.Combobox(self.frameComboAno, width = 15 , textvariable = self.escolhaComboAno)
      self.comboboxAno.pack(side="left")
      self.comboboxAno['values'] = controle.getAnosGastos()
      self.escolhaComboAno.set("")

      #criação do botao de consulta que gera o grafico
      self.buttonSubmit = tk.Button(self.frameButton, text="Consultar")
      self.buttonSubmit.pack(side="left")
      self.buttonSubmit.bind("<Button>", controle.consultaGastoDeputadoHandler)

#view da consulta dos gastos dos partidos
class LimiteconsultaGastoPartido(tk.Toplevel):
    def __init__(self, controle):
      tk.Toplevel.__init__(self)
      self.geometry('1100x750')
      self.title("Consulta Gasto por Partido")
      self.controle = controle

      #criação dos frames
      self.frameComboPartido = tk.Frame(self)
      self.frameComboAno = tk.Frame(self)
      
      self.frameComboPartido.pack()
      self.frameComboAno.pack()

      self.frameButton = tk.Frame(self)
      self.frameButton.pack()

      #criação das labels
      self.labelComboPartido = tk.Label(self.frameComboPartido, text="Partido: ")
      self.labelComboPartido.pack(side="left")

      self.labelComboAno = tk.Label(self.frameComboAno, text="Ano: ")
      self.labelComboAno.pack(side="left")

      #criação das comboboxes
      self.escolhaComboPartido = tk.StringVar()
      self.comboboxPartido = ttk.Combobox(self.frameComboPartido, width = 15, textvariable = self.escolhaComboPartido)
      self.comboboxPartido.pack(side="left")
      self.comboboxPartido['values'] = controle.getSiglasPartidos()
      self.escolhaComboPartido.set("")

      #configuracao das comboboxes
      self.escolhaComboAno = tk.StringVar()
      self.comboboxAno = ttk.Combobox(self.frameComboAno, width = 15 , textvariable = self.escolhaComboAno)
      self.comboboxAno.pack(side="left")
      self.comboboxAno['values'] = controle.getAnosGastos()
      self.escolhaComboAno.set("")

      #criação do botao de consulta que gera o grafico
      self.buttonSubmit = tk.Button(self.frameButton, text="Consultar")
      self.buttonSubmit.pack(side="left")
      self.buttonSubmit.bind("<Button>", controle.consultaGastoPartidoHandler)

#view da consulta dos partidos que mais gastaram dinheiro da cota
class LimiteverPartMaisGastam(tk.Toplevel):
    def __init__(self, controle):
      tk.Toplevel.__init__(self)
      self.geometry('1100x750')
      self.title("Consulta Gasto por Partido")
      self.controle = controle

      sql = ''' SELECT dep.siglapartido, sum(gas.valorliquido) FROM deputados dep, gastos gas
        WHERE gas.id_deputado = dep.id AND gas.ano = 2022 GROUP BY dep.siglapartido ORDER BY sum(gas.valorliquido) DESC LIMIT 5; '''
       
      df_gastos = pd.DataFrame(consultar_db(sql),  columns=['partido', 'valor'])
      figure = plt.Figure(figsize=(8,6), dpi=100)

      x = df_gastos['partido']
      y = df_gastos['valor'].apply(float)
  
      ax = figure.add_subplot(111)
      ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
      #previnindo notação cientifica
      ax.ticklabel_format(style='plain', axis='y')
      chart_type = FigureCanvasTkAgg(figure, self)
      chart_type.get_tk_widget().pack()
      ax.set_title('Partidos que mais gastaram')

class LimitepopularBanco(tk.Toplevel):
  def __init__(self, controle):
      tk.Toplevel.__init__(self)
      self.geometry('350x200')
      self.title("Popular ou atualizar banco")
      self.controle = controle

      #criando frame do input de usuario e senha
      self.frameNome = tk.Frame(self)
      self.frameNome.pack()
      self.frameSenha = tk.Frame(self)
      self.frameSenha.pack()

      #criando label do input
      self.labelNome = tk.Label(self.frameNome, text="Usuario: ")
      self.labelNome.pack(side="left")
      self.labelSenha = tk.Label(self.frameSenha, text="Senha: ")
      self.labelSenha.pack(side="left")

      #criando input
      self.inputNome = tk.Entry(self.frameNome, width=20)
      self.inputNome.pack()
      self.inputSenha = tk.Entry(self.frameSenha, show='*', width=20)
      self.inputSenha.pack()

      #criação dos frames dos botões
      self.frameButtonPopularDep = tk.Frame(self)
      self.frameButtonPopularDep.pack()
      self.frameButtonPopularDetalhesDep = tk.Frame(self)
      self.frameButtonPopularDetalhesDep.pack()
      self.frameButtonPopularDiscursos = tk.Frame(self)
      self.frameButtonPopularDiscursos.pack()
      self.frameButtonPopularPartidos = tk.Frame(self)
      self.frameButtonPopularPartidos.pack()
      self.frameButtonPopularGastos = tk.Frame(self)
      self.frameButtonPopularGastos.pack()

      #criação do botao de popular a tabela deputados
      self.buttonPopularDep = tk.Button(self.frameButtonPopularDep, text="Popular Deputados")
      self.buttonPopularDep.pack(side="left")
      self.buttonPopularDep.bind("<Button>", controle.popularDeputados)

      #criação do botao de popular os detalhes dos deputados na tabela deputados
      self.buttonPopularDetalhesDep = tk.Button(self.frameButtonPopularDetalhesDep, text="Popular Detalhes dep.")
      self.buttonPopularDetalhesDep.pack(side="left")
      self.buttonPopularDetalhesDep.bind("<Button>", controle.popularDetalhesDeputados)

      #criação do botao de popular os discursos feitos pelos deputados na tabela discursos
      self.buttonPopularDiscursos = tk.Button(self.frameButtonPopularDiscursos, text="Popular Discursos")
      self.buttonPopularDiscursos.pack(side="left")
      self.buttonPopularDiscursos.bind("<Button>", controle.popularDiscursos)

      #criação do botao de popular os partidos dos deputados na tabela partidos
      self.buttonPopularPartidos = tk.Button(self.frameButtonPopularPartidos, text="Popular Partidos")
      self.buttonPopularPartidos.pack(side="left")
      self.buttonPopularPartidos.bind("<Button>", controle.popularPartidos)

      #criação do botao de popular os gastos a partir do json que esta no diretorio do codigo,
      #tive que baixar completo esses dados e trata-los para o BD
      self.buttonPopularGastos = tk.Button(self.frameButtonPopularGastos, text="Popular Gastos")
      self.buttonPopularGastos.pack(side="left")
      self.buttonPopularGastos.bind("<Button>", controle.popularGastos)

   




