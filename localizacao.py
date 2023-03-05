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
from itertools import chain
import re
from tabelas import url_base
from sqlalchemy import insert,select
import pandas as pd
from tabelas import teste



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


def reader_excel():
    lista_dicts = []
    driver.implicitly_wait(4)
    df = pd.read_excel(r"C:\Users\Guilh\OneDrive\Área de Trabalho\urls001.xlsx")
    listas = df['urls'].to_list()
    for lista in listas:
        
        time.sleep(5)
        driver.get(lista)
        dict_items = {}

        scroll_page()

        
        try:
            dict_items['URL'] = lista
            coordenadas = driver.find_elements(By.XPATH,'/html/body/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div')
            for coordenada in coordenadas:
                
                dict_items['Caracteristicasloja'] = coordenada.get_attribute("textContent")
        
                dict_items['Latitude'] = coordenada.get_attribute("data-lat")
                dict_items['Longitude'] = coordenada.get_attribute("data-lng")
                dict_items['ref'] = coordenada.get_attribute("data-id")
                dict_items['id'] = coordenada.get_attribute("id")
                
              

                engine = mssq_datawharehouselocal()
                with engine.connect() as conn:
                        result = conn.execute(insert(teste)
                                        ,[{"caracteristica":dict_items['Caracteristicasloja']
                                        ,"latitude":dict_items['Latitude'],"url":dict_items['URL']
                                        ,"longitude":dict_items['Longitude']
                                        ,"id":dict_items['id'],"ref":dict_items['ref']}])


                print(dict_items)

        except:
            pass
    
reader_excel()

