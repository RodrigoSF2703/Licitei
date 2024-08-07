import os
import requests
import pyautogui as pg
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import simpledialog
import logging
import time
import random

# Configuração de logs para registrar informações importantes durante a execução
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações para a API e o caminho do WebDriver
API_URL = os.getenv("API_URL", "https://app.licitei.co/api/rest/biddings")
API_KEY = os.getenv("API_KEY", "eyJhbGciOiJIUzI1NiJ9")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, 'resources', 'chromedriver-win64', 'chromedriver.exe')
REMOTE_DEBUGGING_PORT = 9222


def open_chrome():
    """Abre o navegador Google Chrome com depuração remota."""
    try:
        # Inicia o Chrome com a porta de depuração remota
        pg.press('win')
        time.sleep(random.uniform(1, 5))
        pg.write('cmd', interval=0.1)
        pg.press('enter')
        time.sleep(random.uniform(1, 2))
        pg.write(f'chrome.exe --remote-debugging-port={REMOTE_DEBUGGING_PORT} --user-data-dir="C:/ChromeDebug"')
        pg.press('enter')
        time.sleep(random.uniform(2.5, 3.5))
    except Exception as e:
        logger.error(f"Erro ao abrir o Chrome: {e}")


def insert_target_url():
    """Insere a URL de destino no navegador."""
    try:
        pg.moveTo(451, 64)
        time.sleep(random.uniform(1, 5))
        pg.click()
        time.sleep(random.uniform(2, 5))
        pg.typewrite('https://www.gov.br/compras/pt-br')
        time.sleep(random.uniform(2, 5))
        pg.press('enter')
    except Exception as e:
        logger.error(f"Erro ao inserir a URL: {e}")


def page_navigation():
    """Navega na página especificada."""
    try:
        pg.moveTo(1390, 120)
        pg.click()
        time.sleep(random.uniform(3, 5))
        pg.moveTo(1278, 652)
        time.sleep(random.uniform(3, 5))
        pg.click()
        time.sleep(random.uniform(3, 5))
    except Exception as e:
        logger.error(f"Erro na navegação da página: {e}")


def start_selenium():
    """Inicia o navegador Selenium conectado a uma sessão existente."""
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{REMOTE_DEBUGGING_PORT}")
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    return driver


def fetch_api_data(url, key):
    """Busca dados da API.

    Args:
        url (str): URL da API.
        key (str): Chave da API.

    Returns:
        dict: Dados retornados pela API ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na solicitação dos detalhes dos acordos: {e}")
        return None


def random_delay(min_seconds=1, max_seconds=3):
    """Adiciona um atraso aleatório.

    Args:
        min_seconds (int): Mínimo de segundos de atraso.
        max_seconds (int): Máximo de segundos de atraso.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def input_box(message, title):
    """Exibe uma caixa de entrada de texto usando Tkinter.

    Args:
        message (str): Mensagem a ser exibida na caixa de entrada.
        title (str): Título da caixa de entrada.

    Returns:
        str: Entrada do usuário.
    """
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring(title, message)
    root.destroy()
    return user_input


def human_click(driver, element):
    """Função para clicar em um elemento de forma 'humana'.

    Args:
        driver (webdriver): Instância do WebDriver.
        element (WebElement): Elemento a ser clicado.
    """
    action = webdriver.ActionChains(driver)
    action.move_to_element(element)
    action.pause(random.uniform(0.5, 1.5))
    action.click()
    action.perform()
    random_delay()


def human_wait_and_click(driver, xpath, label):
    """Função para esperar e clicar em um elemento, simulando comportamento humano.

    Args:
        driver (webdriver): Instância do WebDriver.
        xpath (str): XPath do elemento a ser clicado.
        label (str): Descrição do elemento para logs.

    Returns:
        bool: True se o elemento foi encontrado e clicado, False caso contrário.
    """
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        human_click(driver, element)
        return True
    except Exception as e:
        logger.error(f"{label} não encontrado: {e}")
        return False


def select_certificate(driver, assunto_desejado):
    """Função para selecionar o certificado digital desejado.

    Args:
        driver (webdriver): Instância do WebDriver.
        assunto_desejado (str): Texto do certificado desejado.

    Returns:
        bool: True se o certificado foi encontrado e selecionado, False caso contrário.
    """
    try:
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        main_window = driver.current_window_handle
        cert_window = [window for window in driver.window_handles if window != main_window][0]
        driver.switch_to.window(cert_window)

        timeout = time.time() + 30
        found = False
        while time.time() < timeout and not found:
            certificate_list = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='certificateList']//li"))
            )

            for certificate in certificate_list:
                cert_text = certificate.text
                logger.info(f"Verificando certificado: {cert_text}")
                if assunto_desejado in cert_text:
                    certificate.click()
                    found = True
                    break
            else:
                driver.execute_script("arguments[0].scrollIntoView();", certificate_list[-1])
                time.sleep(1)

        if not found:
            logger.error("Certificado com o assunto desejado não encontrado.")
            return False

        if not human_wait_and_click(driver, '//button[text()="OK"]', 'Botão OK'):
            return False

        driver.switch_to.window(main_window)
        return True
    except Exception as e:
        logger.error(f"Erro ao selecionar certificado: {e}")
        return False


def main():
    """Função principal do script."""
    try:
        # Busca dados da API
        api_data = fetch_api_data(API_URL, API_KEY)
        if not api_data:
            return

        # Pede ao usuário para inserir o CPF desejado
        cpf_desejado = input_box("Digite o CPF para consulta:", "Entrada de CPF")

        # Procura pelo CPF desejado nos dados da API
        for details in api_data:
            user_data = details.get("user", {})
            if user_data.get("cpf") == cpf_desejado:
                assunto = user_data.get("companyName")
                quantidade_items = len(details.get("items", []))
                logger.info(f"Quantidade de itens: {quantidade_items}")

                # Abre o Chrome e navega para a URL desejada
                open_chrome()
                insert_target_url()
                page_navigation()

                # Inicia o Selenium WebDriver e se conecta à sessão do navegador existente
                driver = start_selenium()

                # Seleciona o certificado digital
                if not select_certificate(driver, assunto):
                    return

                # Clica no elemento especificado pelo XPath
                element = driver.find_element(By.XPATH, '//*[@id="ccfd3198-e29b-4f7e-b28f-3e741ad999e6"]/div')
                element.click()

                break
        else:
            logger.warning(f"CPF não encontrado nos detalhes dos acordos.")
    finally:
        pass


if __name__ == '__main__':
    main()
