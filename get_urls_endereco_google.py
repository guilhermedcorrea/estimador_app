

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


def get_anuncios():
    listas= []
    driver.implicitly_wait(6)
    df = pd.read_excel(r"C:\Users\Guilh\OneDrive\Área de Trabalho\urlsdeenderecos.xlsx")
    dicts = df.to_dict('records')
    for keys in dicts:
        time.sleep(4)
        driver.get(keys['urls'])

  
        scroll_page()
        cards = driver.find_elements(By.XPATH,'//*[@id="rl_ist0"]/div/div[2]/div/table//a')
        for card in cards:
            dict = {}
            card.text
            dict['urls'] = card.get_attribute("href")
            listas.append(dict)
            print(card.get_attribute("href"))

    df = pd.DataFrame(listas)
    df.to_excel(r"C:\Users\Guilh\OneDrive\Área de Trabalho\farmaciasurlsgoogle0008.xlsx")



def get_infos():
    listas = []
    driver.implicitly_wait(6)
    df = pd.read_excel(
        r"C:\Users\Guilh\OneDrive\Área de Trabalho\farmaciasurlsgoogle0008.xlsx")
    new_dict = df.to_dict("records")

    time.sleep(1)
    for dicts in new_dict:
        driver.get(dicts['urls'])

        time.sleep(15)

        scroll_page()
        try:
            valores = driver.find_elements(
                By.XPATH,"//div[@jscontroller='AtSb']")
            valor_ref = driver.find_elements(
                By.XPATH,"/html/body/div[6]/div/div[9]/div[1]/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div[1]/div[3]/div/div[1]")
            cont = 0
            for valor in valores:
                dict = {}
                dict["Atributos"] = valor.text
                dict["latitude"] = valor_ref[cont].get_attribute("data-lat")
                dict["Longitude"] = valor_ref[cont].get_attribute("data-lng")
                listas.append(dict)
                cont+=1
                
                print(dict)
        except:
            pass
            
    df = pd.DataFrame(listas)
    df.to_excel(r"C:\Users\Guilh\OneDrive\Área de Trabalho\farmaciasurlsgoogle00082222.xlsx")





get_infos()



