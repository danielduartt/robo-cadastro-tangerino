import sys
import os
from dotenv import load_dotenv

# --- Correção de Import ---
# Adiciona o diretório raiz do projeto ao path para encontrar a pasta 'src'
# e permitir que os módulos se encontrem.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
# -------------------------

# Importações do Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Importa as funções que vamos testar em sequência
from src.login.login import realizar_login
from cadastro import navegar_para_colaboradores, iniciar_novo_cadastro

# --- CONFIGURAÇÕES DO TESTE ---
URL_LOGIN = "https://app.tangerino.com.br/Tangerino/pages/LoginPage"

def testar_abertura_formulario():
    """
    Script que testa o fluxo completo até a abertura do formulário de cadastro.
    """
    print("--- INICIANDO TESTE DE ABERTURA DO FORMULÁRIO ---")
    
    load_dotenv()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        meu_usuario = os.getenv("TANGERINO_USER")
        minha_senha = os.getenv("TANGERINO_PASS")
        
        if not meu_usuario or not minha_senha:
            print("ERRO: Credenciais não encontradas no arquivo .env. Verifique o arquivo.")
            return

        # Etapa 1: Realizar o login
        driver.get(URL_LOGIN)
        if not realizar_login(driver, wait, meu_usuario, minha_senha):
            print("\n❌ FALHA NO TESTE: O login falhou.")
            return

        # Etapa 2: Navegar para a página de colaboradores
        if not navegar_para_colaboradores(driver, wait):
            print("\n❌ FALHA NO TESTE: A navegação para colaboradores falhou.")
            return

        # Etapa 3: Clicar em "Cadastrar" para abrir o formulário
        # Esta é a função que você selecionou e que estamos testando.
        if iniciar_novo_cadastro(driver, wait):
            print("\n✅ TESTE BEM-SUCEDIDO: Formulário de cadastro aberto com sucesso!")
        else:
            print("\n❌ FALHA NO TESTE: Não foi possível abrir o formulário de cadastro.")

    except Exception as e:
        print(f"\n❌ ERRO FATAL NO SCRIPT DE TESTE: {e}")
        driver.get_screenshot_as_file("erro_fatal_formulario.png")
        print("   Screenshot 'erro_fatal_formulario.png' salvo.")

    finally:
        driver.quit()
        print("--- TESTE FINALIZADO ---")

if __name__ == "__main__":
    testar_abertura_formulario()

