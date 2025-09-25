import sys
import os
import time
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
CAMINHO_PLANILHA = "data/colaborador_unico.xlsx" # Planilha com dados de apenas um colaborador

def testar_simulacao_unica():
    """
    Script que testa o preenchimento do formulário para um único colaborador,
    sem salvar, permitindo verificação visual.
    """
    print("--- INICIANDO TESTE DE SIMULAÇÃO DE CADASTRO ÚNICO ---")
    
    load_dotenv()
    
    chrome_options = Options()
    # A linha '--headless' foi removida para que o navegador seja visível durante o teste.
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized") # Inicia o navegador maximizado
    
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
            print("\n❌ FALHA NA SIMULAÇÃO: O login falhou.")
            return

        # Etapa 2: Navegar para Colaboradores
        if not navegar_para_colaboradores(driver, wait):
            print("\n❌ FALHA NA SIMULAÇÃO: A navegação para colaboradores falhou.")
            return

        # Etapa 3: Executar o preenchimento a partir da planilha (em modo de teste)
        # Passar modo_teste=True garante que o robô NÃO clicará em "Salvar".
        if executar_cadastros_planilha(driver, wait, CAMINHO_PLANILHA, modo_teste=True):
            print("\n✅ SIMULAÇÃO BEM-SUCEDIDA: Formulário preenchido para verificação.")
            print("   O navegador ficará aberto por 30 segundos.")
            time.sleep(30) # Pausa para verificação visual
        else:
            print("\n❌ FALHA NA SIMULAÇÃO: Ocorreram erros durante o preenchimento.")

    except Exception as e:
        print(f"\n❌ ERRO FATAL NO SCRIPT DE TESTE: {e}")
        driver.get_screenshot_as_file("erro_fatal_simulacao_unica.png")
        print("   Screenshot 'erro_fatal_simulacao_unica.png' salvo.")

    finally:
        driver.quit()
        print("--- TESTE FINALIZADO ---")

if __name__ == "__main__":
    testar_simulacao_unica()

