import os
import requests
from botcity.web import WebBot, Browser
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import simpledialog
import logging
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

# Configuração de logs para registrar informações importantes durante a execução
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações para a API e o caminho do WebDriver
API_URL = os.getenv("API_URL", "https://app.licitei.co/api/rest/biddings")
API_KEY = os.getenv("API_KEY", "eyJhbGciOiJIUzI1NiJ9")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, 'resources', 'chromedriver-win64', 'chromedriver.exe')

# Permite que o script continue mesmo se não estiver conectado ao Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


# Função para buscar dados da API
def fetch_api_data(url, key):
    headers = {
        "Content-Type": "application/json",
        "api-key": key
    }
    try:
        # Faz uma requisição GET para a API
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na solicitação dos detalhes dos acordos: {e}")
        return None


# Função para configurar o WebBot com as opções necessárias
# Função para configurar o WebBot com as opções necessárias
def setup_bot():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Redefine o User-Agent para parecer uma navegação normal
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Instala o ChromeDriver e retorna o caminho do executável
    chrome_driver_path = ChromeDriverManager().install()

    # Inicializa o WebBot com o navegador Chrome e as opções configuradas
    bot = WebBot(headless=False)
    bot.driver_path = chrome_driver_path
    bot.chrome_options = chrome_options
    bot.start_browser()


    return bot


# Função para desativar a detecção de automação
def disable_automation_detection(bot):
    bot.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


# Função para adicionar um atraso aleatório
def random_delay():
    time.sleep(random.uniform(1, 3))


# Função para clicar em um elemento de forma "humana"
def human_click(bot, element):
    action = ActionChains(bot.driver)
    action.move_to_element(element)
    action.pause(random.uniform(0.5, 1.5))  # Pausa aleatória entre 0.5 e 1.5 segundos
    action.click()
    action.perform()


# Função para esperar e clicar em um elemento, simulando comportamento humano
def human_wait_and_click(bot, xpath, label):
    try:
        element = WebDriverWait(bot.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        human_click(bot, element)
        return True
    except Exception as e:
        logger.error(f"{label} não encontrado: {e}")
        return False


# Função para simular uma navegação humana ao carregar um URL
def browse_like_human(bot, url):
    bot.driver.get(url)
    time.sleep(random.uniform(2, 5))  # Espera aleatória para simular leitura da página


# Função para selecionar o certificado digital desejado
def select_certificate(bot, assunto_desejado):
    try:
        # Espera até que a janela do certificado seja aberta
        WebDriverWait(bot.driver, 10).until(EC.number_of_windows_to_be(2))
        main_window = bot.driver.current_window_handle
        cert_window = [window for window in bot.driver.window_handles if window != main_window][0]
        bot.driver.switch_to.window(cert_window)

        # Timeout de 30 segundos para encontrar o certificado
        timeout = time.time() + 30
        found = False
        while time.time() < timeout and not found:
            certificate_list = WebDriverWait(bot.driver, 10).until(
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
                # Desce a página para carregar mais certificados
                bot.driver.execute_script("arguments[0].scrollIntoView();", certificate_list[-1])
                time.sleep(1)

        if not found:
            logger.error("Certificado com o assunto desejado não encontrado.")
            return False

        if not human_wait_and_click(bot, '//button[text()="OK"]', 'Botão OK'):
            return False

        bot.driver.switch_to.window(main_window)
        return True
    except Exception as e:
        logger.error(f"Erro ao selecionar certificado: {e}")
        return False


# Função para exibir uma caixa de entrada de texto usando Tkinter
def input_box(message, title):
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring(title, message)
    root.destroy()
    return user_input


# Função principal do script
def main():
    # Inicializa o Maestro SDK
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    logger.info(f"Task ID is: {execution.task_id}")
    logger.info(f"Task Parameters are: {execution.parameters}")

    # Configura e desativa a detecção de automação no bot
    bot = setup_bot()
    disable_automation_detection(bot)
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

                # Acessa o site gov.br/compras simulando navegação humana
                browse_like_human(bot, 'https://www.gov.br/compras/pt-br')

                # Realiza os cliques necessários para login
                if not human_wait_and_click(bot, '//*[@id="barra-sso"]', 'Entrar com o gov.br'):
                    return
                if not human_wait_and_click(bot, '//*[@id="login-certificate"]', 'Login com Certificado Digital'):
                    return

                # Seleciona o certificado digital
                if not select_certificate(bot, assunto):
                    return

                # Acessa o sistema
                if not human_wait_and_click(bot, '//*[@id="card0"]/div/div/div/div[2]/button', 'Acesso ao sistema'):
                    return

                break
        else:
            logger.warning(f"CPF não encontrado nos detalhes dos acordos.")
    finally:
        # Fecha o navegador ao final da execução
        bot.driver.quit()


if __name__ == '__main__':
    main()
