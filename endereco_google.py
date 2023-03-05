

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



def get_enderecos_concorrente():
    lista_urls = []
    driver.implicitly_wait(3)
  
    try:
        df = pd.read_csv(
            r"C:\Users\Guilh\OneDrive\Documentos\GitHub\google_shopping\urlsfranquias0001.csv",sep=";")
        dicts = df.to_dict("records")
        for dic in dicts:
            driver.get(dic['url_estado'])
            time.sleep(16)
            nomes = driver.find_elements(By.CLASS_NAME,'rllt__details')
            for nom in nomes:
                dict_enderecs = {}
                listas = nom.text
                dict_enderecs['Enderecos'] = listas
                dict_enderecs['urls'] = dic['url_estado']
                lista_urls.append(dict_enderecs)

                print(len(listas),listas)
            
    except:
        pass

    df = pd.DataFrame(lista_urls)
    df.to_csv("lista_enderecos_estados2222.csv")

get_enderecos_concorrente()