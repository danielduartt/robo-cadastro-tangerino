import sys
import os
from dotenv import load_dotenv

# Adiciona o diretório raiz do projeto ao path para encontrar a pasta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Importações do Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Importa as funções dos nossos módulos
from src.login.login import realizar_login
from src.cadastro.cadastro import navegar_para_colaboradores, executar_cadastros_planilha

# --- CONFIGURAÇÕES DO TESTE ---
URL_LOGIN = "https://app.tangerino.com.br/Tangerino/pages/LoginPage"
CAMINHO_PLANILHA = "data/colaborador_unico.xlsx" 

def testar_cadastro_unico():
    """
    Script que testa o cadastro de um único colaborador do início ao fim.
    """
    print("--- INICIANDO TESTE DE CADASTRO ÚNICO ---")
    
    load_dotenv()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Aumenta o tempo de espera geral para 30 segundos
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        meu_usuario = os.getenv("TANGERINO_USER")
        minha_senha = os.getenv("TANGERINO_PASS")
        
        if not meu_usuario or not minha_senha:
            print("ERRO: Credenciais não encontradas no arquivo .env.")
            return

        # Etapa 1: Login
        driver.get(URL_LOGIN)
        if not realizar_login(driver, wait, meu_usuario, minha_senha):
            print("\n❌ FALHA NO TESTE: O login falhou.")
            return

        # Etapa 2: Navegar para Colaboradores
        if not navegar_para_colaboradores(driver, wait):
            print("\n❌ FALHA NO TESTE: A navegação para colaboradores falhou.")
            return

        # Etapa 3: Executar o cadastro a partir da planilha (em modo real)
        # Omitir o modo_teste ou passá-lo como False executará o salvamento.
        if executar_cadastros_planilha(driver, wait, CAMINHO_PLANILHA):
            print("\n✅ TESTE BEM-SUCEDIDO: Processo de cadastro finalizado.")
        else:
            print("\n❌ FALHA NO TESTE: Ocorreram erros durante o processo de cadastro.")

    except Exception as e:
        print(f"\n❌ ERRO FATAL NO SCRIPT DE TESTE: {e}")
        driver.get_screenshot_as_file("erro_fatal_cadastro_unico.png")
        print("   Screenshot 'erro_fatal_cadastro_unico.png' salvo.")

    finally:
        driver.quit()
        print("--- TESTE FINALIZADO ---")

if __name__ == "__main__":
    testar_cadastro_unico()
