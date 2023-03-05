from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
import re
from itertools import chain
from itertools import chain,zip_longest
import pandas as pd
from config import mssq_datawharehouselocal
from sqlalchemy import insert, select
from tabelas import urls_franquia,atributos_franchising



def insert_franquias(*args, **kwargs):
    engine = mssq_datawharehouselocal()
    with engine.connect() as conn:
            result = conn.execute(insert(atributos_franchising)
                            ,[{"nome":kwargs["nome_franquia"]
                            ,"investimento_minimo":kwargs["InvestimentoInicial"],"total_unidades":kwargs["TotalUnidades"]
                            ,"retorno":kwargs["Retorno"],"sede":kwargs["EstadoSede"]
                            ,"url":kwargs["url_anuncio"],"id_franquia":int(kwargs["id_franquia"])}])

          
       

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


def investimento_inicial(args):
    for arg in args:
        investimento = re.findall(r"([R$]\d+\.\d+)+",arg)
        if len(investimento) !=0:
            return investimento
         

def tempo_retorno(args):
    for arg in args:
        retorno = re.findall(r"([de ]\d+[a]\d+)([ meses])+", arg)
        if len(retorno) !=0:
            return retorno
           

def total_unidades(args):
    for arg in args:
        unidades = re.findall(r"([NÚUMERO DE UNIDADES]+)(\s+\d+)+",arg)
        if len(unidades) !=0:
            return unidades
           
       
def estado_sede(args):
    for arg in args:
        sede = re.findall(r"(\bESTADO SEDE \b)([A-Z-ÃÁÍÚÓ]+)",arg)
        if len(sede) !=0:
            return sede
           

def extract_item():
    driver.implicitly_wait(5)
    try:
        value = driver.find_elements(By.XPATH,'/html/body/div/div[1]/div/div[2]')
        for val in value:
            dict_items = {}
            strs = val.text.strip().split("\n")
            if next(filter(lambda k: len(k.strip()) > 0, strs)):
                dict_items['Atributos'] = strs
               
                t_unidades = total_unidades(strs)
                dict_items['TotalUnidades'] = t_unidades

                i_inicial = investimento_inicial(strs)
                dict_items['InvestimentoInicial'] = i_inicial
                e_sede = estado_sede(strs)
                dict_items['EstadoSede'] = e_sede

                t_retorno = tempo_retorno(strs)
                dict_items['TempoRetorno'] = t_retorno

            return dict_items
                
  
    except:
        pass

def get_urls():
    lista_dicts = []
    engine = mssq_datawharehouselocal()
    with engine.connect() as conn:
        get_item = conn.execute(select(urls_franquia.c.nome_franquia
                                       ,urls_franquia.c.url_anuncio
                                       ,urls_franquia.c.categoria,
                                       urls_franquia.c.faixa_preco,
                                       urls_franquia.c.id_franquia)).all()
        
        dict_tems = [row._asdict() for row in get_item]
        n = len(dict_tems)
        i = 0
        new_dict_item = {}
        while i < n:
            
            driver.get(dict_tems[i]['url_anuncio'])
                
            new_dict = extract_item()

            try:
                nome = driver.find_elements(
                        By.XPATH,'/html/body/div/div[1]/div/div[2]/div[1]/div//h1')[0].text
                new_dict_item['NomeFranquia'] = nome
                   
            except:
                pass
                
            try:
                retorno = driver.find_elements(
                        By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[1]/div[1]/div[2]/div/div/strong')[0].text
                new_dict_item['Retorno'] = retorno
            except:
                pass

            new_dict_item['url_anuncio'] = dict_tems[i]['url_anuncio']
            new_dict_item['categoria']  = dict_tems[i]['categoria']
            new_dict_item['faixa_preco']  = dict_tems[i]['faixa_preco']
            new_dict_item['nome_franquia']  = dict_tems[i]['nome_franquia']
            new_dict_item['id_franquia'] = dict_tems[i]['id_franquia']

            try:
                new_dict_item['InvestimentoInicial'] = str(
                    new_dict['InvestimentoInicial']).replace("['$","").replace("']","").strip()
            except:
                pass
            
        
            try:
                new_dict_item['TotalUnidades'] = str(
                    new_dict['TotalUnidades']).split(",")[-1].replace("'","").replace("'","").replace(")]","").strip()
            except:
                pass

            try:
                new_dict_item['EstadoSede'] = str(
                    new_dict['EstadoSede']).split(",")[-1].replace("')]","").replace("'","").strip().capitalize()
            except:
                pass

            try:
                clica1 = driver.find_element(By.ID,'Quiosques').click()
            except:
                pass

            time.sleep(1)

            try:
                quiosques = driver.find_elements(By.CLASS_NAME,'tab-content Quiosques')
                quisq = [item.text.split("\n") for item in quiosques]
                print(quisq)
                new_dict['Quiosqueatributos'] = quisq
                
            except Exception as e:
                print(e)

            time.sleep(1)

            try:
                clica = driver.find_element(By.ID,'Lojas').click()
            except:
                pass

            try:
                loja = driver.find_elements(By.ID,'leftColMinisite')
                lojas = [item.text.split("\n") for item in loja]
                new_dict['LojaAtributo'] = lojas
                print(lojas)
            except:
                pass
            

            print(new_dict)

            yield new_dict
        

                
            '''
            try:
                insert_franquias(url_anuncio=new_dict_item['url_anuncio'],nome_franquia=new_dict_item['NomeFranquia']
                                ,InvestimentoInicial=new_dict_item['InvestimentoInicial'],TotalUnidades=new_dict_item['TotalUnidades']
                                ,EstadoSede=new_dict_item['EstadoSede'],Retorno=new_dict_item['Retorno'],id_franquia=new_dict_item['id_franquia'])

            except Exception as e:
                print(e)
            '''

            i+=1

lista_dicts = []
dicts = get_urls()
for dict in dicts:
    lista_dicts.append(dict)

df = pd.DataFrame(lista_dicts)
df.to_excel("dadosfranquiaslojas.xlsx")
    
