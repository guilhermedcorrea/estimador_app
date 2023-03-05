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
from tabelas import urls_franquia



def insert_url_base(*args, **kwargs):
    engine = mssq_datawharehouselocal()
    with engine.connect() as conn:
        
        
        if conn.execute(select(urls_franquia.c.nome_franquia).where(urls_franquia.c.nome_franquia == kwargs['nome_franquia'])).first():

            print("Já existe",kwargs["url_anuncio"])
        else:
            print("Cadastrando",kwargs["url_anuncio"])
            try:
                result = conn.execute(insert(urls_franquia)
                            ,[{"id_franquia":kwargs["id_franquia"],"url_anuncio":kwargs["url_anuncio"]
                            ,"url_base":kwargs["url_base"],"categoria":kwargs["categoria"]
                            ,"faixa_preco":kwargs["faixa_preco"],"nome_franquia":kwargs["nome_franquia"]}])
                            
            except Exception as e:

                print("error", e)
       

options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options,
                             executable_path=r'C:\Users\Guilherme\Documents\google_shopping\chromedriver\chromedriver.exe')


def scroll_page() -> None:
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(1)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True


def get_links():
    lista_urls = []
    driver.implicitly_wait(5)


    driver.get("https://franquias.portaldofranchising.com.br/franquia-com-selo-de-excelencia/")
   
    scroll_page()
    time.sleep(3)
    dict_item = {}
 
    urls = driver.find_elements(By.XPATH,'/html/body/div/div[2]/div/div[2]/div/div/a')
    cont = 0
    for url in urls: 
        url_ = url.get_attribute("href")
        dict_item['UrlFranquia'] = url_
        title = url.get_attribute("title")
        dict_item['NomeFranquia'] = title
        id = url.get_attribute("data-id")
        dict_item['IdFranquia'] = id
        faixa = driver.find_elements(By.XPATH,'/html/body/div/div[2]/div/div[2]/div/div/a/div[2]//p')
            
        dict_item['FaixaInvestiMento'] = faixa[cont].text
        dict_item['UlPrincipal'] = 'https://franquias.portaldofranchising.com.br/franquia-com-selo-de-excelencia/'
        dict_item['Categoria'] = 'Franquias com selo de Excelencia'
            
        cont+=1
          
        insert_url_base(id_franquia=dict_item['IdFranquia']
                            ,url_anuncio=dict_item['UrlFranquia'],url_base=dict_item['UlPrincipal']
                            ,categoria=dict_item['Categoria'],faixa_preco=str(dict_item['FaixaInvestiMento']).strip()
                            ,nome_franquia=str(dict_item['NomeFranquia']).strip().capitalize())
           
            


   

get_links()

def get_franchising():
    lista_dicts = []
    driver.implicitly_wait(5)
    lista_urls = get_links()
    for lista in lista_urls:
        driver.get(lista['PaginaUrl'])
        time.sleep(1)

        dict_franchising = {

                "Url":lista["PaginaUrl"],
                "Categoria":lista["Categoria"],
                "NomeFRanquia":lista["NomeFranquia"],
                "PaginaFranquia":lista['PaginaUrl']

            }

        attrs = driver.find_elements(By.ID,'leftColMinisite')
        for att in attrs:
            items = att.text
            scroll_page()

            try:
                nome = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[1]/h1')[0].text
                dict_franchising['Nome'] = nome
            except:
                pass

            try:
                tempo_retorno = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[1]/div[1]/div[2]/div/div/strong')[0].text
                dict_franchising['TempoRetorno'] = tempo_retorno
            except:
                pass

            try:
                inestimento_inicial = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[1]/div[1]/div[1]/div/div/strong')[0].text
                dict_franchising['InvestimentoInicial'] = inestimento_inicial
            except:
                pass

            try:
                unidades_pelo_brasil = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[1]/div[1]/div[3]/div/div/strong')[0].text
                if re.search('[R$]',unidades_pelo_brasil):
                    pass
                else:
                    dict_franchising['UnidadesBrasil'] = unidades_pelo_brasil
              
            except:
                pass

            try:
                clicar = driver.find_element(By.ID,'Lojas').click()
            except:
                pass

            time.sleep(1)
            try:
                clicar_ = driver.find_element(By.ID,'Quiosques').click()
            except:
                pass
            
            lista_itens = []
            try:
                informacoes_quisque = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]')
                for infos in informacoes_quisque:
                    values = infos.text
                    lista_itens.append(values)
            except:
                pass
        

            dict_franchising["CaracteristicasGerais_2"] = lista_itens
            try:
                lista_atributos = []
                informaces_gerais = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[2]')
                for informacoes in informaces_gerais:
                    lista_atributos.append(informacoes.text)
            except:
                pass
            dict_franchising["CaracteristicasGerais"] = lista_atributos
            
            try:
                pagina_franquia = driver.find_elements(By.XPATH,'//*[@id="leftColMinisite"]/div/div/div[2]/div/div[3]/div[2]/a')[0].get_attribute("href")
                dict_franchising['PaginaFranquia'] = pagina_franquia
            except:
                pass


            

            print(dict_franchising)
            lista_dicts.append(dict_franchising)

    df = pd.DataFrame(lista_dicts)
    #df.to_csv("teste.csv")
           




#get_franchising()
