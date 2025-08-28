import sys
import csv
import os
import re
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer


class INPIApp(QWidget):

    def __init__(self, lista_processos):
        super().__init__()
        self.setWindowTitle("INPI busca automática")
        self.setGeometry(100, 100, 1200, 800)

        # lista de processos já filtrados (somente 9 dígitos)
        self.lista_processos = lista_processos
        self.index_atual = 0  # controla o processo atual
        self.login_executado = False

        # Layout principal
        layout_principal = QHBoxLayout()
        self.setLayout(layout_principal)

        # ----- Lado esquerdo: lista + botão -----
        conteudo_layout = QVBoxLayout()

        # Lista de processos
        self.lista_widget = QListWidget()
        self.lista_widget.addItems(self.lista_processos)
        conteudo_layout.addWidget(self.lista_widget)

        # Botão para iniciar a busca
        self.btn_login = QPushButton("Iniciar busca")
        self.btn_login.setFixedHeight(30)
        self.btn_login.clicked.connect(self.fazer_login)
        conteudo_layout.addWidget(self.btn_login)

        layout_principal.addLayout(conteudo_layout, stretch=2)

        # ----- Lado direito: navegador -----
        self.webview = QWebEngineView()
        layout_principal.addWidget(self.webview, stretch=4)

        # URLs
        self.url_inpi = "https://busca.inpi.gov.br/pePI/"
        self.url_destino = (
            "https://busca.inpi.gov.br/pePI/jsp/marcas/Pesquisa_num_processo.jsp"
        )

        self.webview.load(QUrl(self.url_inpi))
        self.webview.loadFinished.connect(self.on_page_load)

    def fazer_login(self):
        """Inicia o processo de busca"""
        self.login_executado = True
        self.webview.reload()

    def on_page_load(self, ok):
        if not ok:
            return

        url_atual = self.webview.url().toString()

        if self.login_executado and url_atual == self.url_inpi:
            # login fake -> só redireciona para a tela de pesquisa
            self.webview.load(QUrl(self.url_destino))
            self.login_executado = False

        elif url_atual == self.url_destino:
            # Se ainda tiver processos, pesquisa o próximo
            if self.index_atual < len(self.lista_processos):
                processo = self.lista_processos[self.index_atual]
                print(f"🔎 Pesquisando processo: {processo}")

                js_preencher_processo = f"""
                (function(){{
                    var campo = document.getElementsByName('NumPedido')[0];
                    if(campo){{
                        campo.value = "{processo}";
                        var btn = document.querySelector('input[type="submit"]');
                        if(btn) btn.click();
                    }}
                }})()
                """
                self.webview.page().runJavaScript(js_preencher_processo)

            else:
                print("✅ Todas as pesquisas foram concluídas!")

        else:
            # Captura o HTML para verificar resultado
            self.webview.page().toHtml(self.verificar_resultado)

    def verificar_resultado(self, html):
        # Expressão regular para capturar número do processo
        padrao_numero = re.compile(
            r"<td align=\"center\">\s*<font class=\"normal\">\s*<a [^>]+>\s*(\d+)\s*</a>",
            re.IGNORECASE,
        )

        # Expressão regular para capturar situação do processo
        padrao_situacao = re.compile(
            r"<td class=\"left padding-5\">\s*<font class=\"normal\">\s*(.*?)\s*</font>",
            re.IGNORECASE | re.DOTALL,
        )

        numeros = padrao_numero.findall(html)
        situacoes = padrao_situacao.findall(html)

        # Lista para armazenar processos filtrados
        processos_validos = []

        # Verifica correspondência
        for num, situacao in zip(numeros, situacoes):
            situacao = situacao.strip()
            if "Verificando o pagamento da concessão" in situacao:
                print(f"✅ Processo {num} com situação: {situacao}")
                processos_validos.append(num)
            else:
                print(f"⚠️ Processo {num} sem situação correspondente: {situacao}")

        # Salva os processos filtrados em CSV
        if processos_validos:
            with open(
                "processos_filtrados.csv", "a", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                for processo in processos_validos:
                    writer.writerow([processo])

        # Avança para o próximo processo
        self.index_atual += 1
        QTimer.singleShot(500, lambda: self.webview.load(QUrl(self.url_destino)))


def carregar_processos(caminho_csv: str):
    """Lê o CSV e retorna a lista de processos"""
    processos = []
    with open(caminho_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # ignora linhas vazias
                processos.append(row[0])  # pega a única coluna
    return processos


if __name__ == "__main__":
    caminho_csv = os.path.join("ui", "numeros_extraidos.csv")
    processos = carregar_processos(caminho_csv)
    print("📂 Processos carregados do CSV:")
    for p in processos:
        print(p)

    app = QApplication(sys.argv)
    window = INPIApp(processos)
    window.show()
    sys.exit(app.exec_())
