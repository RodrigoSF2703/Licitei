import time
import requests
from botcity.web import WebBot, Browser, By
from botcity.maestro import BotMaestroSDK
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


def get_api_data(api_url, api_key):
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Erro na solicitação dos detalhes dos acordos: {err}")
        return None


def select_certificate(bot, cpf_desejado):
    # Aguarda até que a lista de certificados seja exibida
    WebDriverWait(bot.driver, 10).until(
        EC.number_of_windows_to_be(2)
    )

    # Alterna para a janela do certificado
    main_window = bot.driver.current_window_handle
    cert_window = [window for window in bot.driver.window_handles if window != main_window][0]
    bot.driver.switch_to.window(cert_window)

    try:
        certificate_list = WebDriverWait(bot.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='certificateList']//li"))
        )
    except:
        print("Lista de certificados não encontrada.")
        return False

    # Itera pela lista de certificados e seleciona aquele que contém o CPF desejado
    for certificate in certificate_list:
        if cpf_desejado in certificate.text:
            certificate.click()
            break
    else:
        print("Certificado com o CPF desejado não encontrado.")
        return False

    # Clica no botão OK para confirmar a seleção do certificado
    try:
        btn_ok = WebDriverWait(bot.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
        )
        btn_ok.click()
    except:
        print("Botão OK não encontrado.")
        return False

    # Volta para a janela principal
    bot.driver.switch_to.window(main_window)
    return True


def main():
    # Inicializa Maestro SDK
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    # Inicializa WebBot
    bot = WebBot()
    bot.headless = False
    bot.browser = Browser.CHROME
    bot.driver_path = r"C:\Users\drigo\PycharmProjects\Licitei\liciteiCompras\resources\chromedriver-win64\chromedriver.exe"

    api_url = "https://app.licitei.co/api/rest/biddings"
    api_key = "eyJhbGciOiJIUzI1NiJ9"

    # Obtém dados da API
    all_details_data = get_api_data(api_url, api_key)
    if not all_details_data:
        return

    cpf_desejado = input("Digite o CPF para consulta: ")

    for details_data in all_details_data:
        if details_data.get("login").get("cpf") == cpf_desejado:
            # Abre o navegador e faz login no gov.br
            bot.browse('https://www.gov.br/compras/pt-br')

            # Clica em 'Entrar com o gov.br'
            try:
                btn_gov = WebDriverWait(bot.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="barra-sso"]'))
                )
                btn_gov.click()
            except:
                not_found('Entrar com o gov.br')
                return

            # Clica em 'Login com Certificado Digital'
            try:
                btn_certificate = WebDriverWait(bot.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="login-certificate"]'))
                )
                btn_certificate.click()
            except:
                not_found('Login com Certificado Digital')
                return

            # Seleciona o certificado com o CPF desejado
            if not select_certificate(bot, cpf_desejado):
                return

            # Clica 'Acesso ao sistema'
            try:
                btn_access_system = WebDriverWait(bot.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="card0"]/div/div/div/div[2]/button'))
                )
                btn_access_system.click()
            except:
                not_found('Acesso ao sistema')
                return

            # Passos futuros a serem adicionados

            break
    else:
        print(f"CPF não encontrado nos detalhes dos acordos.")


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()