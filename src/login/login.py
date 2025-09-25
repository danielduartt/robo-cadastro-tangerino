from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def realizar_login(driver, wait, usuario, senha):
    """
    Função responsável por realizar o login no sistema, agora com
    lógica para lidar com conteúdo dentro de um <embed> (iframe).
    """
    try:
        print("-> Módulo de Login: Preenchendo informações...")

        seletor_css_email = "input[name='login'][placeholder='Digite o e-mail']"
        campo_email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_css_email)))
        campo_email.clear()
        campo_email.send_keys(usuario)
        print("   Campo de e-mail preenchido.")

        seletor_css_senha = "input[name='password'][placeholder='Digite aqui sua senha']"
        campo_senha = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_css_senha)))
        campo_senha.clear()
        campo_senha.send_keys(senha)
        print("   Campo de senha preenchido.")

        xpath_seletor_botao = "//input[@value='Entrar']"
        botao_login = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_seletor_botao)))
        botao_login.click()
        print("   Botão de login clicado.")
        
        # --- CORREÇÃO PARA CONTEÚDO EMBUTIDO (IFRAME) ---
        print("   Aguardando o carregamento do painel principal (embed)...")
        # 1. Espera o elemento <embed> aparecer na página principal
        embed_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "embed")))
        
        # 2. Muda o foco do Selenium para o conteúdo do <embed>
        driver.switch_to.frame(embed_element)
        print("   Foco alterado para o painel.")

        # 3. Agora, dentro do <embed>, procura pela confirmação de login
        xpath_confirmacao = "//h3[contains(., 'EMSERH!')]"
        wait.until(EC.presence_of_element_located((By.XPATH, xpath_confirmacao)))
        print("   Texto de confirmação encontrado no painel.")
        
        # 4. Retorna o foco para a página principal para os próximos passos
        driver.switch_to.default_content()
        print("   Foco retornado para a página principal.")
        # ---------------------------------------------------
        
        print("-> Módulo de Login: Login realizado com sucesso!")
        return True
        
    except TimeoutException as e:
        # --- BLOCO DE DEPURAÇÃO ---
        print("\n❌ ERRO: TimeoutException. Um elemento demorou demais para aparecer.")
        screenshot_path = "debug_falha_login.png"
        driver.get_screenshot_as_file(screenshot_path)
        print(f"   [DEBUG] Screenshot salvo em: '{screenshot_path}'")
        
        html_path = "debug_pagina.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"   [DEBUG] Código HTML da página salvo em: '{html_path}'")
        return False

    except Exception as e:
        # Captura de outros erros inesperados
        print(f"-> Módulo de Login: Falha inesperada ao realizar o login. Erro: {e}")
        driver.get_screenshot_as_file("debug_erro_inesperado.png")
        return False

