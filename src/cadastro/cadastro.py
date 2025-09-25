import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def navegar_para_colaboradores(driver, wait):
    """
    Navega pelo menu principal até a página de listagem de colaboradores.
    """
    try:
        print("-> Módulo de Cadastro: Iniciando navegação para 'Colaboradores'.")
        # É preciso garantir que o foco está na página principal para clicar nos menus
        driver.switch_to.default_content()
        
        menu_principal_xpath = "//a[.//span[contains(text(), 'Cadastros gerais')]]"
        wait.until(EC.element_to_be_clickable((By.XPATH, menu_principal_xpath))).click()
        print("   Clicado em 'Cadastros gerais'.")
        
        submenu_colaboradores_xpath = "//a[.//span[text()='Colaboradores']]"
        wait.until(EC.element_to_be_clickable((By.XPATH, submenu_colaboradores_xpath))).click()
        print("   Clicado em 'Colaboradores'.")

        # Após clicar, o conteúdo da lista é carregado dentro do <embed>
        # Vamos mudar o foco para dentro do <embed> para encontrar o botão
        print("   Aguardando o painel de colaboradores carregar...")
        embed_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "embed")))
        driver.switch_to.frame(embed_element)
        
        wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
        print("   Página de colaboradores encontrada com sucesso (dentro do painel).")
        return True
    except Exception as e:
        print(f"❌ ERRO ao navegar para a página de colaboradores: {e}")
        driver.get_screenshot_as_file("debug_falha_navegacao.png")
        # Garante que o foco volte ao padrão em caso de erro
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False

def iniciar_novo_cadastro(driver, wait):
    """
    Na tela de listagem (JÁ DENTRO DO PAINEL), clica em "Cadastrar" e aguarda o formulário.
    """
    try:
        print("-> Módulo de Cadastro: Clicando no botão para iniciar novo cadastro.")
        # O driver já deve estar focado no painel/embed por causa da função anterior
        wait.until(EC.element_to_be_clickable((By.ID, "editPageLink"))).click()
        
        # Confirma que o formulário foi aberto verificando o campo "Nome"
        # O formulário abre dentro do mesmo painel/embed
        wait.until(EC.presence_of_element_located((By.NAME, "nome")))
        print("   Formulário de cadastro aberto com sucesso.")
        return True
    except Exception as e:
        print(f"❌ ERRO ao tentar abrir o formulário de cadastro: {e}")
        driver.get_screenshot_as_file("debug_falha_abrir_formulario.png")
        return False

def preencher_formulario_colaborador(driver, wait, linha):
    """
    Preenche os campos do formulário (JÁ DENTRO DO PAINEL).
    """
    try:
        print("   Preenchendo o formulário...")
        # Inputs de texto
        wait.until(EC.presence_of_element_located((By.NAME, "nome"))).send_keys(linha['Nome Completo'])
        driver.find_element(By.NAME, "email").send_keys(linha['Email'])
        driver.find_element(By.NAME, "dataNascimento").send_keys(linha['Data de Nascimento'])
        driver.find_element(By.NAME, "telefone").send_keys(str(linha['Telefone']))
        driver.find_element(By.NAME, "cpf").send_keys(str(linha['CPF']))
        driver.find_element(By.NAME, "dataAdmissao").send_keys(linha['Data Admissao'])
        driver.find_element(By.NAME, "dataInicioVigencia").send_keys(linha['Inicio Vigencia'])
        driver.find_element(By.NAME, "idExterno").send_keys(str(linha['Cod. Externo']))

        # Select boxes
        Select(wait.until(EC.presence_of_element_located((By.NAME, "cargo")))).select_by_visible_text(linha['Cargo'])
        Select(wait.until(EC.presence_of_element_located((By.NAME, "empresa")))).select_by_visible_text(linha['Filial'])
        Select(wait.until(EC.presence_of_element_located((By.NAME, "tipoVinculo")))).select_by_visible_text(linha['Tipo de Vinculo'])
        
        # Lógica especial para Local de Trabalho
        Select(wait.until(EC.presence_of_element_located((By.ID, "selectedLocalTrabalho")))).select_by_visible_text(linha['Local de Trabalho'])
        driver.find_element(By.NAME, "btnAddLocalTrabalho").click()
        
        print("   Formulário preenchido.")
        return True
    except Exception as e:
        print(f"   ❌ ERRO durante o preenchimento do formulário: {e}")
        driver.get_screenshot_as_file("debug_erro_preenchimento.png")
        return False

def executar_cadastros_planilha(driver, wait, caminho_arquivo_dados, modo_teste=False):
    """
    Orquestra o processo de cadastro a partir de uma planilha.
    Se modo_teste=True, apenas preenche o formulário sem salvar.
    """
    try:
        df = pd.read_excel(caminho_arquivo_dados)
        print(f"\n-> Módulo de Cadastro: {len(df)} colaboradores encontrados na planilha.")
        
        for index, linha in df.iterrows():
            nome = linha['Nome Completo']
            print(f"\n--- Iniciando {'simulação de' if modo_teste else ''} cadastro de: {nome} ---")
            
            # Etapa 1: Abrir o formulário de cadastro.
            # A função navegar_para_colaboradores já deixou o foco dentro do painel.
            if not iniciar_novo_cadastro(driver, wait):
                print(f"   ❌ ERRO: Não foi possível abrir o formulário para {nome}. Interrompendo.")
                # Antes de sair, retorna o foco para a página principal
                driver.switch_to.default_content()
                return False

            # Etapa 2: Preencher o formulário
            if not preencher_formulario_colaborador(driver, wait, linha):
                # Tenta voltar para a lista para continuar com o próximo colaborador
                try:
                    # O botão Voltar está dentro do mesmo painel/embed
                    driver.find_element(By.ID, "id2da").click()
                    wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
                except:
                    print("   Não foi possível retornar à página de listagem. Interrompendo.")
                    driver.switch_to.default_content()
                    return False
                continue

            # Etapa 3: Salvar (ou não, se for teste)
            if not modo_teste:
                driver.find_element(By.ID, "id2d8").click() # Botão Salvar
                print("   Botão 'Salvar' clicado.")
                
                # A mensagem de sucesso aparece dentro do mesmo painel/embed
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Operação realizada com sucesso')]")))
                print(f"   ✅ SUCESSO: {nome} cadastrado!")

                # Após salvar, o sistema geralmente volta para a lista automaticamente.
                # Vamos esperar o botão 'Cadastrar' da lista aparecer novamente.
                wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
                print("   Retorno para a lista de colaboradores confirmado.")
            else:
                print("   Simulação concluída. O botão 'Salvar' NÃO foi clicado.")
                # Em modo de teste, paramos após o primeiro para permitir a verificação.
                # Retornamos o foco para a página principal antes de sair.
                driver.switch_to.default_content()
                return True
                
        # Após o loop, retorna o foco para a página principal
        driver.switch_to.default_content()
        return True

    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de dados '{caminho_arquivo_dados}' não foi encontrado.")
        return False
    except Exception as e:
        print(f"❌ ERRO FATAL no processo de cadastro em lote: {e}")
        driver.get_screenshot_as_file("debug_erro_fatal_cadastro.png")
        # Garante que o foco volte ao padrão em caso de erro
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False

