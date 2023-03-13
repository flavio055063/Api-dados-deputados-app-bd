Este código em python possui uma interface gráfica feita com Tkinter, e é uma aplicação didática. Nessa aplicação, é consumido dados de uma API governamental sobre os
deputados federais, guardando essas informações no banco de dados PostgreSQL. É possível gerar gráficos a partir dos dados coletados.

Para rodar o código em python, primeiro é necessário criar o banco de dados com o postgres (conforme o arquivo .sql disponibilizado)

Depois, é só executar o main.py e popular o banco de dados (para popular a tabela gastos, vc precisa obter o json e coloca-lo no diretorio onde esta rodando seu arquivo python)

Caso prefira, você pode recriar o banco a partir do backup disponibilizado.

O json para os gastos podem ser acessados atraves do arquivo zipado ou baixados no link: 
https://dadosabertos.camara.leg.br/swagger/api.html#staticfile

Veja o código na função de inserir gastos para tirar duvidas (no arquivo Deputados.py)

O vídeo de explicação está no link: https://youtu.be/Szef5xqjmcI
