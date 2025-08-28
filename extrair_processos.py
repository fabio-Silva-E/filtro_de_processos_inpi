import os
import re
import csv
from PyPDF2 import PdfReader


def extrair_numeros_do_pdf(caminho_pdf: str):
    numeros = []
    reader = PdfReader(caminho_pdf)

    for i, page in enumerate(reader.pages, start=1):
        texto = page.extract_text()
        if not texto:
            continue

        matches = re.findall(r"(\d+)\s+Deferimento do pedido", texto)
        numeros.extend(matches)

        print(f"   📄 Página {i}: {len(matches)} números encontrados")

    return numeros


def criar_pasta_pdf():
    pasta = os.path.join("ui", "pdfs_to_read")
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        print(f"✅ Pasta criada: {pasta}")
    else:
        print(f"📂 Pasta já existe: {pasta}")
    return pasta


def processar_pdfs_existentes():
    pasta = criar_pasta_pdf()
    arquivos = [f for f in os.listdir(pasta) if f.endswith(".pdf")]

    if not arquivos:
        print("⚠️ Nenhum PDF encontrado na pasta para processar.")
        return

    todos_numeros = []

    for arquivo in arquivos:
        caminho_pdf = os.path.join(pasta, arquivo)
        print(f"\n🔍 Processando: {arquivo}")
        numeros = extrair_numeros_do_pdf(caminho_pdf)
        print(f"✅ Total extraído de {arquivo}: {len(numeros)} números")
        todos_numeros.extend(numeros)

    if todos_numeros:
        salvar_csv(todos_numeros)
    else:
        print("⚠️ Nenhum número encontrado em nenhum PDF.")


def salvar_csv(numeros):
    caminho_csv = os.path.join("ui", "numeros_extraidos.csv")
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        for numero in numeros:
            writer.writerow([numero])

    print(f"\n💾 Arquivo CSV salvo em: {caminho_csv}")
    print(f"📊 Total de números salvos: {len(numeros)}")


if __name__ == "__main__":
    processar_pdfs_existentes()
