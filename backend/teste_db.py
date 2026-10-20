import mysql.connector
from config import DB_CONFIG

try:
    conexao = mysql.connector.connect(**DB_CONFIG)

    if conexao.is_connected():
        print("Conexão com o MySQL estabelecida!")

    conexao.close()

except mysql.connector.Error as erro:
    print(f"Erro ao conectar com o MySQL: {erro}")