

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
    lista_mobli = []
    driver.get("https://www.mobly.com.br/loja-mobly/")
    driver.implicitly_wait(4)
    
    
    iframe = driver.find_element(By.ID,'storelocator')
    driver.switch_to.frame(iframe)


    try:
        scroll_page()
        time.sleep(3)
        enderecos = driver.find_elements(By.XPATH,'//*[@id="listagem"]/div//p')
        for endereco in enderecos:
            endereco_ = endereco.text
            enderecos_dict = {}
            if re.findall(r'\,\s+\w+', endereco_):
                enderecos_dict['enderecos'] = endereco_
                lista_mobli.append(enderecos_dict)
                
            
    except Exception as e:
        print(e)
    driver.switch_to.default_content()
    df = pd.DataFrame(lista_mobli)
    df.to_csv("enderecos_mobli.csv")




get_urls()


   
    



















#https://www.mobly.com.br/loja-mobly/