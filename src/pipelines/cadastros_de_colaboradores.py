# main.py

import time
from getpass import getpass

from login import realizar_login
from cadastro import cadastrar_colaboradores

# Importações do Selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Importa as NOSSAS funções dos outros arquivos
from login import realizar_login
from cadastro import cadastrar_colaboradores

# --- CONFIGURAÇÕES GLOBAIS ---
URL_LOGIN = "https://app.tangerino.com.br/Tangerino/pages/LoginPage/" # <-- MUDE AQUI
ARQUIVO_DADOS = "colaboradores.xlsx"

def main():
    """
    Função principal que orquestra a execução do robô.
    """
    # --- INICIALIZAÇÃO DO SELENIUM ---
    print("Iniciando o robô...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 20)
    
    try:
        # Pede as credenciais de forma segura
        meu_usuario = input("Digite seu usuário de login: ")
        minha_senha = getpass("Digite sua senha: ")

        # --- EXECUÇÃO DO FLUXO ---
        driver.get(URL_LOGIN)
        driver.maximize_window()

        # 1. Chama a função de login
        login_sucesso = realizar_login(driver, wait, meu_usuario, minha_senha)

        # 2. Se o login funcionou, chama a função de cadastro
        if login_sucesso:
            cadastrar_colaboradores(driver, wait, ARQUIVO_DADOS)
        else:
            print("Não foi possível continuar com o cadastro, pois o login falhou.")

    finally:
        # --- FINALIZAÇÃO ---
        print("\nProcesso finalizado. O navegador será fechado em 10 segundos.")
        time.sleep(10)
        driver.quit() # Garante que o navegador sempre será fechado

# --- PONTO DE ENTRADA DO SCRIPT ---
# Garante que o código dentro deste if só rode quando executamos "python main.py"
if __name__ == "__main__":
    main()