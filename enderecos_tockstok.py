

from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
import re
from typing import Literal, List, Generator
from itertools import chain
from sqlalchemy import text
from config import mssql_get_conn as myboxengine,mssq_datawharehouselocal
from itertools import chain, zip_longest
from tabelas import url_base,google_shopping
from sqlalchemy import insert, select
import pandas as pd


options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options,
                               executable_path=r'C:\Users\Guilherme\Documents\google_shopping\chromedriver\chromedriver.exe')





time.sleep(1)


def scroll_page() -> None:
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(1)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True


def get_urls():
    lista_urls = []
    driver.get("https://www.tokstok.com.br/lojas")

    driver.implicitly_wait(4)
    time.sleep(1)
    scroll_page()
    urls = driver.find_elements(By.XPATH,
                                "/html/body/div[2]/div/div[1]/div/div[6]/div/div[2]/div/section/div/div[4]/div/div[1]/section/div/div/div//a")
  
    for url in urls:
        urls_lojas = url.get_attribute('href')
        lista_urls.append(urls_lojas)
    return lista_urls

def get_enderecos():
    lista_enderecos_dict = []
    driver.implicitly_wait(4)
    urls_loja = get_urls()
    for url in urls_loja:
        dict_endereco = {}
        driver.get(url)
        time.sleep(1)

        try:
            cidade = driver.find_elements(
                By.XPATH,'/html/body/div[2]/div/div[1]/div/div[6]/div/div[2]/div/section/div/div/div/div[3]/section/div[3]/h3')[0].text
            print(cidade)
            dict_endereco['Cidade'] = cidade
        except Exception as e:
            print(e)
        

        try:
            enderecos = driver.find_elements(
                By.XPATH,"/html/body/div[2]/div/div[1]/div/div[6]/div/div[2]/div/section/div/div/div/div[3]/section/div[4]/div[1]/p[1]")[0].text
            print(enderecos)
            dict_endereco['Logradouro'] = enderecos
        except Exception as e:
            print(e)

        dict_endereco['url_endereco'] = url

        lista_enderecos_dict.append(dict_endereco)

    df = pd.DataFrame(lista_enderecos_dict)
    df.to_csv("enderecos_tock_stock.csv")


get_enderecos()