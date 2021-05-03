from selenium import webdriver
from selenium.webdriver import ChromeOptions
import reclameaqui
from time import sleep
import datetime as dt
import json
import re
#import xlsxwriter
import argparse
import pandas as pd

def parsing_routine():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('--original_file','-o')

    return parser.parse_args()

def popular_excel(dicionario):

    wb = pd.ExcelWriter(args.output_file)

    lista_empresas = list(dicionario.keys())
    
    if args.original_file:
        old_wb = pd.ExcelFile(args.original_file)
        lista_sheets = old_wb.sheet_names
        lista_empresas.extend(x for x in lista_sheets if x not in lista_empresas)
    
    for empresa in lista_empresas:
        dados = pd.DataFrame()
        try:
            dados = dados.append(pd.read_excel(args.original_file, sheet_name=empresa))    
        except:
            pass
        
        try:
            dicionario_pandas = pd.DataFrame(dicionario.get(empresa), columns=['título','link','dados','descrição','data'])
            dicionario_pandas.dados.apply(lambda x: ' - '.join(x))
            dados = dados.append(dicionario_pandas)
        except:
            pass
        
        dados.drop_duplicates(subset=['link'], inplace=True)
        dados.to_excel(wb, sheet_name=empresa, index=False)

    wb.close()

        
args = parsing_routine()

with open(args.input_file, encoding='utf-8') as file:
    j = json.load(file)

options = ChromeOptions()
options.headless = False
options.add_argument("--start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-automation'])

PATH = r'D:\programas\executables\chromedriver.exe'

palavras_base = j['dados'][0]['palavras']
                              
dicionario = {}

for i in range(1, len(j['dados'])):
    
    dado = j['dados'][i]
    grupo = dado['nome']
    palavras = palavras_base + dado['palavras']
    links = [l[0] for l in dado['link']]
    paginas = [l[1] for l in dado['link']]
    data_inicio = dt.datetime.strptime(dado['data'], '%Y/%m/%d')

    for e, empresa in enumerate(links):

        driver = webdriver.Chrome(PATH, options = options)
        driver.maximize_window()
        
        c = reclameaqui.ReclameAqui(driver, empresa)
        sleep(1)      
        c.extrair_informacoes(paginas[e])
        sleep(1)
        c.extrair_descricoes()
        
        dicionario.update(c.verificar_palavras(palavras))

        driver.quit()

popular_excel(dicionario)

