# cadastro.py (Versão atualizada com a sua pipeline)

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def cadastrar_colaboradores(driver, wait, caminho_arquivo_dados):
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