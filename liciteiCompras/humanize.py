import pyautogui as pg
import time
import random


# Função para clicar no botão Iniciar, pesquisar pelo Google Chrome e abrir o navegador
def open_chrome():
    # Clicar no botão Iniciar do Windows
    pg.press('win')
    time.sleep(random.uniform(1, 5))
    pg.write('Google Chrome', interval=0.1)
    pg.press('enter')
    time.sleep(random.uniform(2.5, 3.5))
'''
    pg.keyDown('win')
    time.sleep(0.5)
    pg.press('up')
    pg.keyUp('win')

    time.sleep(1.5)
'''
def insert_target_url():
    pg.moveTo(451, 64)
    time.sleep(random.uniform(1, 5))
    pg.click()
    time.sleep(random.uniform(2, 5))
    pg.typewrite('https://www.gov.br/compras/pt-br')
    time.sleep(random.uniform(2, 5))
    pg.press('enter')

def page_navigation():
    pg.moveTo(1390, 120)
    pg.click()
    time.sleep(random.uniform(3, 5))
    pg.moveTo(1278, 652)
    #pg.write("11386889679", interval=random.uniform(0.1, 0.6))
    time.sleep(random.uniform(3, 5))
    # pg.press("enter")
    pg.click()
    time.sleep(random.uniform(3, 5))
    # pg.write("Kctb2cwst54c12xotb422!", interval=random.uniform(0.1, 0.6))
    # time.sleep(random.uniform(1, 3))
    # pg.press("enter")

'''
    pg.moveTo(1302, 648)
    pg.click()
    time.sleep(1)
'''

'''
# Executar a função
open_chrome()
insert_target_url()
page_navigation()
'''