import pandas as pd
import pyodbc


# Configuração da conexão com SQL Server
def conectar_sqlserver():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=192.168.3.4,1433;"
        "DATABASE=INPI_Busca;"
        "UID=admin;"
        "PWD=24098675"
    )


# Função para salvar os processos
def salvar_processos_sqlserver(processos):
    conn = conectar_sqlserver()
    cursor = conn.cursor()

    for numero in processos:
        cursor.execute("INSERT INTO processos (Numero_Processo) VALUES (?)", (numero,))

    conn.commit()
    conn.close()
    print(f"{len(processos)} processos salvos com sucesso no banco!")


if __name__ == "__main__":
    # Lê o CSV sem cabeçalho, cria a coluna "numero_processo"
    df = pd.read_csv("processos_filtrados.csv", header=None, names=["numero_processo"])

    # Pega todos os processos (sem filtro)
    processos = df["numero_processo"].tolist()

    print("Processos carregados:", processos)

    # Salva no banco
    salvar_processos_sqlserver(processos)
