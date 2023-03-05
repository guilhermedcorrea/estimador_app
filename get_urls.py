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
from googletb import url_base_seller_ecommerce
from sqlalchemy import insert,select



def get_produtos():
    enginemssql = myboxengine()

    with enginemssql.begin() as conn:
        call = (text("""SELECT DISTINCT produto.id,produto.nome as nomeproduto,produto.marca ,produto.fabricanteId
            ,produto.codigoFabricante,produto.CodigoBarras,produto.categoriaId,categoria.nome as categoria
            FROM [myboxmarcenaria].[dbo].[Produto] as produto
            inner join [myboxmarcenaria].[dbo].[Categoria] as categoria
            on categoria.id = produto.categoriaId
            WHERE  produto.id in (
            SELECT vitem.produtoId
            from venda VENDAS
            left join myboxmarcenaria.dbo.Unidade AS LOJA ON LOJA.id = VENDAS.unidadeId
            left join dbo.VendaItem as vitem
            on vitem.vendaId = VENDAS.id
            WHERE LOJA.id not in(1, 85, 89, 127)
            and LOJA.excluido = 0
            and VENDAS.statusId > 2
            and VENDAS.excluido = 0
            and VENDAS.numeracao <> 0)"""))
        
        excel = conn.execute(call).all()

        dict_tems = [row._asdict() for row in excel]
        yield dict_tems
      

options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options,
                               executable_path=r'C:\Users\Guilherme\Documents\google_shopping\chromedriver\chromedriver.exe')




def extract_urls_google(*args, **kwargs):

    url_seller = driver.find_elements(
        By.XPATH,'//*[@id="rso"]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/a')
    for urls in url_seller:
        urlg_g = urls.get_attribute("href").split("hl=pt")[0]
        if urlg_g !=None:
            dict_item = {
                "google_url":urlg_g,
                "id_produto":kwargs['id_produto'],
                "nomeproduto":kwargs["nomeproduto"],
                "codigo_barras":kwargs["codigo_barras"],
                "fabricanteid":kwargs["fabricanteid"],
                "codigo_fabricante":kwargs["codigo_fabricante"],
                "categoriaid":kwargs["categoriaid"],
                "nomecategoria":kwargs["nomecategoria"]}
            
            engine = mssq_datawharehouselocal()
            with engine.connect() as conn:

                if conn.execute(select(url_base_seller_ecommerce.c.cod_barras).where(url_base_seller_ecommerce.c.cod_barras == dict_item["codigo_barras"])).first():
                     print("ja existe")
                else:
                    try:
                        print("Inserted", dict_item['codigo_barras'])
                        result = conn.execute(insert(url_base_seller_ecommerce)
                                            ,[{"ref_produto":dict_item["id_produto"],"cod_barras":dict_item["codigo_barras"]
                                            ,"codigoFabricante":dict_item["codigo_fabricante"],"url_base":dict_item["google_url"]
                                            ,"ref_categoria":dict_item["categoriaid"]}])
                        print(dict_item)
                                            
                    except Exception as e:
                                print("error", e)

           
def get_google_urls():
    
    urls_produtos = get_produtos()
    urls_produto = [{**args} for args in chain.from_iterable(urls_produtos)]
    
    n = len(urls_produto)
    i = 1

    while i < n:
        if re.search('[0-9]{9,14}',urls_produto[i]['CodigoBarras']):
            urls_google = str(urls_produto[i]['CodigoBarras']).split(",")[0].strip()


            driver.implicitly_wait(4)
            driver.get("https://shopping.google.com.br/")
          
        
            try:
                name = driver.find_element(By.NAME,'q')
                name.clear()
                name.send_keys(urls_google)

                confirm = driver.find_element(
                    By.XPATH,'//*[@id="kO001e"]/div/div/c-wiz/form/div[2]/div[1]/button/div/span').click()
                
                time.sleep(1)

                extract_urls_google(id_produto =urls_produto[i]['id'], nomeproduto=urls_produto[i]['nomeproduto']
                                    ,fabricanteid=urls_produto[i]['fabricanteId']
                                    ,codigo_fabricante = urls_produto[i]['codigoFabricante']
                                    , categoriaid=urls_produto[i]['categoriaId'], nomecategoria=urls_produto[i]['categoria']
                                    ,codigo_barras=urls_produto[i]['CodigoBarras'])
            except Exception as e:
                print(e)

          
        i+=1


get_google_urls()
    


