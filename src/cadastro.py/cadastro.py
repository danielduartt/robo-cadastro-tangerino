# cadastro.py (Versão atualizada com a sua pipeline)

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def navegar_para_colaboradores(driver, wait):
    """
    Navega pelo menu principal até a página de listagem de colaboradores.
    """
    try:
        print("-> Módulo de Cadastro: Iniciando navegação para 'Colaboradores'.")
        
        # Passo 1: Clicar no menu principal "Cadastros gerais"
        menu_principal_xpath = "//a[.//span[contains(text(), 'Cadastros gerais')]]"
        menu_principal = wait.until(EC.element_to_be_clickable((By.XPATH, menu_principal_xpath)))
        menu_principal.click()
        print("   Clicado em 'Cadastros gerais'.")
        
        # Passo 2: Clicar no submenu "Colaboradores" que aparece em seguida
        submenu_colaboradores_xpath = "//a[.//span[text()='Colaboradores']]"
        submenu_colaboradores = wait.until(EC.element_to_be_clickable((By.XPATH, submenu_colaboradores_xpath)))
        submenu_colaboradores.click()
        print("   Clicado em 'Colaboradores'.")
        
        # Passo 3: Confirmar que a página de filtros carregou, encontrando o botão "Cadastrar"
        # CORREÇÃO: Usando o ID fornecido, que é o seletor mais confiável.
        wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
        print("   Página de colaboradores e botão 'Cadastrar' encontrados com sucesso.")
        
        return True

    except TimeoutException:
        print("\n❌ ERRO: TimeoutException. O robô não conseguiu encontrar um dos menus ou o botão 'Cadastrar' a tempo.")
        print("   Verifique se os seletores estão corretos e se a página carregou.")
        driver.get_screenshot_as_file("debug_falha_navegacao.png")
        print("   [DEBUG] Screenshot 'debug_falha_navegacao.png' salvo.")
        return False
    except Exception as e:
        print(f"-> Módulo de Cadastro: Falha inesperada ao navegar. Erro: {e}")
        driver.get_screenshot_as_file("debug_erro_navegacao.png")
        return False

def iniciar_novo_cadastro(driver, wait):
    """
    Na tela de listagem, clica no botão "Cadastrar" para abrir o formulário.
    """
    try:
        print("-> Módulo de Cadastro: Clicando no botão para iniciar novo cadastro.")
        wait.until(EC.element_to_be_clickable((By.ID, "editPageLink"))).click()
        
        # Confirma que o formulário foi aberto verificando o campo "Nome"
        wait.until(EC.presence_of_element_located((By.NAME, "nome")))
        print("   Formulário de cadastro aberto com sucesso.")
        return True
    except Exception as e:
        print(f"❌ ERRO ao tentar abrir o formulário de cadastro: {e}")
        driver.get_screenshot_as_file("debug_falha_abrir_formulario.png")
        return False

def executar_cadastros_planilha(driver, wait, caminho_arquivo_dados, modo_teste=False):
    """
    Lê os dados de uma planilha e executa o cadastro de cada colaborador.
    Se modo_teste=True, apenas preenche o formulário sem salvar.
    """
    try:
        df = pd.read_excel(caminho_arquivo_dados)
        print(f"\n-> Módulo de Cadastro: {len(df)} colaboradores encontrados na planilha.")
        
        for index, linha in df.iterrows():
            nome = linha['Nome Completo']
            print(f"\n--- Iniciando {'simulação de' if modo_teste else ''} cadastro de: {nome} ---")

            if not iniciar_novo_cadastro(driver, wait):
                print(f"   ❌ ERRO: Não foi possível abrir o formulário para {nome}. Pulando para o próximo.")
                continue

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

                if not modo_teste:
                    # 3. Clica em Salvar
                    driver.find_element(By.ID, "id2d8").click()
                    print("   Botão 'Salvar' clicado.")
                    
                    # 4. Aguarda a mensagem de sucesso
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Operação realizada com sucesso')]")))
                    print(f"   ✅ SUCESSO: {nome} cadastrado!")

                    # 5. Clica em Voltar para retornar à lista
                    driver.find_element(By.ID, "id2da").click()
                    print("   Retornando para a lista de colaboradores.")
                    
                    # 6. Garante que a página de listagem carregou
                    wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
                else:
                    print("   Simulação concluída. O botão 'Salvar' NÃO foi clicado.")
                    # Em modo de teste, paramos após o primeiro para permitir a verificação
                    return True

            except Exception as e_interno:
                print(f"   ❌ ERRO ao processar o cadastro de {nome}: {e_interno}")
                driver.get_screenshot_as_file(f"debug_erro_{nome.replace(' ', '_')}.png")
                try:
                    driver.find_element(By.ID, "id2da").click()
                    wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
                except:
                    print("   Não foi possível retornar à página de listagem. Interrompendo.")
                    return False
                continue
                
        return True

    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de dados '{caminho_arquivo_dados}' não foi encontrado.")
        return False
    except Exception as e:
        print(f"❌ ERRO FATAL no processo de cadastro em lote: {e}")
        return False

    """
    Lê os dados de uma planilha e executa o cadastro de cada colaborador.
    """
    try:
        df = pd.read_excel(caminho_arquivo_dados)
        print(f"\n-> Módulo de Cadastro: {len(df)} colaboradores encontrados na planilha.")
        
        for index, linha in df.iterrows():
            nome = linha['Nome Completo']
            print(f"\n--- Iniciando cadastro de: {nome} ---")

            # 1. Abre um novo formulário de cadastro
            if not iniciar_novo_cadastro(driver, wait):
                print(f"   ❌ ERRO: Não foi possível abrir o formulário para {nome}. Pulando para o próximo.")
                continue

            # 2. Preenche os campos
            try:
                print("   Preenchendo o formulário...")
                wait.until(EC.presence_of_element_located((By.NAME, "nome"))).send_keys(linha['Nome Completo'])
                driver.find_element(By.NAME, "email").send_keys(linha['Email'])
                driver.find_element(By.NAME, "cpf").send_keys(str(linha['CPF']))
                driver.find_element(By.NAME, "dataAdmissao").send_keys(linha['Data Admissao'])
                
                # Para campos <select>, usamos a classe Select
                select_cargo = Select(wait.until(EC.presence_of_element_located((By.NAME, "cargo"))))
                select_cargo.select_by_visible_text(linha['Cargo'])
                print("   Formulário preenchido.")

                # 3. Clica em Salvar
                driver.find_element(By.ID, "id2d8").click()
                print("   Botão 'Salvar' clicado.")
                
                # 4. Aguarda a mensagem de sucesso (ajuste o texto se necessário)
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Operação realizada com sucesso')]")))
                print(f"   ✅ SUCESSO: {nome} cadastrado!")

                # 5. Clica em Voltar para retornar à lista
                driver.find_element(By.ID, "id2da").click()
                print("   Retornando para a lista de colaboradores.")
                
                # 6. Garante que a página de listagem carregou antes de continuar
                wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))

            except Exception as e_interno:
                print(f"   ❌ ERRO ao processar o cadastro de {nome}: {e_interno}")
                driver.get_screenshot_as_file(f"debug_erro_{nome.replace(' ', '_')}.png")
                # Tenta voltar para a listagem para não travar o loop
                try:
                    driver.find_element(By.ID, "id2da").click()
                    wait.until(EC.presence_of_element_located((By.ID, "editPageLink")))
                except:
                    print("   Não foi possível retornar à página de listagem. Interrompendo.")
                    return False
                continue
                
        return True

    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de dados '{caminho_arquivo_dados}' não foi encontrado.")
        return False
    except Exception as e:
        print(f"❌ ERRO FATAL no processo de cadastro em lote: {e}")
        return False
    """
    Função que lê uma planilha e cadastra os colaboradores um a um,
    seguindo o fluxo de Salvar -> Voltar.
    """
    try:
        # Navega para a tela principal de colaboradores ANTES de começar o loop
        print("-> Módulo de Cadastro: Navegando para a tela de colaboradores...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Colaboradores')]"))).click() # Use o seletor correto

        df = pd.read_excel(caminho_arquivo_dados)
        print(f"\n-> Módulo de Cadastro: {len(df)} colaboradores encontrados. Iniciando cadastros...")

        for _, linha in df.iterrows():
            nome = linha['Nome'] # <-- Atenção aos nomes das colunas!
            print(f"--- Cadastrando: {nome} ---")

            try:
                # 1. Clica no botão para iniciar um novo cadastro
                # Este botão deve estar na tela de listagem de colaboradores
                wait.until(EC.element_to_be_clickable((By.ID, "id_do_botao_cadastrar"))).click() # <-- MUDE O SELETOR AQUI

                # 2. Preenche os campos do formulário com os dados da sua planilha
                print("   Preenchendo o formulário...")
                wait.until(EC.presence_of_element_located((By.NAME, "nome_do_campo_nome"))).send_keys(linha['Nome'])
                driver.find_element(By.NAME, "nome_do_campo_cpf").send_keys(str(linha['CPF']))
                driver.find_element(By.NAME, "nome_do_campo_email").send_keys(linha['Email'])
                # ... continue para todos os outros campos da sua planilha
                # driver.find_element(By.NAME, "nome_do_campo_cargo").send_keys(linha['Cargo'])
                # driver.find_element(By.NAME, "nome_do_campo_pin").send_keys(str(linha['PIN']))
                
                # 3. Clica em Salvar
                driver.find_element(By.ID, "id_do_botao_salvar").click() # <-- MUDE O SELETOR AQUI

                # 4. Aguarda a mensagem de sucesso
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "classe_da_mensagem_sucesso")))
                print(f"   ✅ SUCESSO: {nome} salvo!")

                # 5. Clica em Voltar para recomeçar o ciclo
                wait.until(EC.element_to_be_clickable((By.ID, "id_do_botao_voltar"))).click() # <-- MUDE O SELETOR AQUI
                print("   Retornando para a tela de listagem.")

                # Aguarda a tela de listagem carregar antes de iniciar o próximo loop
                wait.until(EC.presence_of_element_located((By.ID, "id_do_botao_cadastrar")))

            except Exception as e_interno:
                print(f"   ❌ ERRO ao cadastrar {nome}: {e_interno}")
                # Recarrega a página de listagem para tentar se recuperar do erro
                driver.refresh()
                continue

    except Exception as e:
        print(f"-> Módulo de Cadastro: Um erro fatal ocorreu. Erro: {e}")