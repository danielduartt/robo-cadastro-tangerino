import time
from getpass import getpass
import sys
import os

from dotenv import load_dotenv
# --- Correção de Import ---
# Adiciona o diretório raiz do projeto (um nível acima de 'src') ao path
# Isso garante que o Python encontre a pasta 'App' para importar o módulo 'login'
# Esta é a forma correta de lidar com imports em projetos com subpastas.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
# -------------------------

# Importações do Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Agora o import do seu módulo de login vai funcionar
from login import realizar_login 

# --- CONFIGURAÇÕES DO TESTE ---
URL_LOGIN = "https://app.tangerino.com.br/Tangerino/pages/LoginPage"

def testar_modulo_de_login():
    """
    Script para testar o módulo de login.
    """
    print("--- INICIANDO TESTE DO MÓDULO DE LOGIN ---")

    # --- ATENÇÃO: PRÉ-REQUISITO FUNDAMENTAL ---
    # Este script SÓ FUNCIONARÁ se o Google Chrome estiver instalado
    # DENTRO do ambiente onde você o executa (no seu caso, o WSL).
    # Verifique com o comando: google-chrome --version
    # Se der "command not found", a automação não irá funcionar.
    # ---------------------------------------------
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080") # Definir um tamanho de janela pode ajudar
    load_dotenv()

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # --- ALERTA DE SEGURANÇA ---
        # A forma correta é pedir a senha ou usar variáveis de ambiente,
        # como explicado no arquivo boas_praticas_seguranca.md.
        # NUNCA deixe a senha diretamente no código em uma versão final.
        meu_usuario = os.getenv("TANGERINO_USER")
        minha_senha = os.getenv("TANGERINO_PASS")
    
        print(f"Acessando: {URL_LOGIN}")
        driver.get(URL_LOGIN)

        sucesso = realizar_login(driver, wait, meu_usuario, minha_senha)

        if sucesso:
            print("\n✅ TESTE BEM-SUCEDIDO: Login realizado com sucesso!")
        else:
            print("\n❌ FALHA NO TESTE: A função de login retornou um erro.")

    except Exception as e:
        print(f"\n❌ ERRO FATAL NO SCRIPT DE TESTE: {e}")
        # Salva um screenshot em caso de erro para ajudar a depurar
        driver.get_screenshot_as_file("erro_fatal.png")
        print("   Screenshot 'erro_fatal.png' salvo.")

    finally:
        driver.quit()
        print("--- TESTE FINALIZADO ---")

if __name__ == "__main__":
    testar_modulo_de_login()
