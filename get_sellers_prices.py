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
from config import mssql_get_conn as myboxengine,mssq_datawharehouse
from itertools import chain, zip_longest
from googletb import google_shopping
from sqlalchemy import insert, select




def get_urls_products():
    engine = mssq_datawharehouse()
    with engine.begin() as conn:
        call = (text("""SELECT url_base,cod_barras
                FROM datawharehouse.extracoes.url_base_seller_ecommerce  """))
        
        excel = conn.execute(call).all()
        dict_tems = [row._asdict() for row in excel]
        yield dict_tems


options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options,
                               executable_path=r'C:\Users\Guilherme\Documents\google_shopping\chromedriver\chromedriver.exe')



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


def extract_sellers(*args, **kwargs):
    driver.implicitly_wait(4)
    scroll_page()
    lista_urls_seller = []
    lista_precos = []
    lista_sellers = []
    try:
        urls_sellers = driver.find_elements(
                By.XPATH,'//*[@id="sh-osd__online-sellers-cont"]/tr/td[1]/div[1]/a')
        for urls in urls_sellers:
            produto_seller_url = urls.get_attribute('href')
            lista_urls_seller.append(produto_seller_url)
                   
    except:
        pass

    try:
        precos = driver.find_elements(
                By.XPATH,'//*[@id="sh-osd__online-sellers-cont"]/tr/td[4]/div/div[1]')
        for preco in precos:
            precop = preco.text.replace("R$","").strip().replace(".","").replace(",",".")
            lista_precos.append(precop)
              
    except:
        pass
            
    try:
        seller_name = driver.find_elements(
                By.XPATH,'//*[@id="sh-osd__online-sellers-cont"]/tr/td[1]/div[1]/a')
        for seller in seller_name:
            lista_sellers.append(seller.text)
                
    except:
        pass
    
 
    sellers = [seller for seller in lista_sellers if seller !=None]
    for i in range(len(sellers)):
        dict_produtos = {
            "url_seller":lista_urls_seller[i],
            "precos":float(lista_precos[i]),
            "sellernames":lista_sellers[i],
            "url_base":kwargs["url_base"],
            "cod_barras":kwargs["cod_barras"]}
        print(dict_produtos)
   

        engine = mssq_datawharehouse()
        with engine.connect() as conn:
                
            
                result = conn.execute(insert(google_shopping)
                                                ,[{"cod_barras":dict_produtos["cod_barras"]
                                                ,"nome_concorrente":dict_produtos["sellernames"],"loja_venda":dict_produtos["sellernames"]
                                                ,"url_loja":dict_produtos["url_seller"],"preco_concorrente":dict_produtos["precos"]
                                                ,"url_google":dict_produtos["url_base"]}])
                        
           

def get_urls_precos_google():
    driver.implicitly_wait(4)
    precos = get_urls_products()
    urls_google = [{**preco} for preco in chain.from_iterable(precos)]
    n = len(urls_google)
    i = 1
    while i < n:
        time.sleep(3)
        driver.get(urls_google[i]['url_base'])
        extract_sellers(url_base = urls_google[i]['url_base'],cod_barras=urls_google[i]['cod_barras'])
        

        i+=1


get_urls_precos_google()