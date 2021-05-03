from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import io
from PIL import Image
import re
import datetime as dt


class ReclameAqui:

    base_url = "https://www.reclameaqui.com.br/empresa/"

    def __init__(self, driver, empresa):
        self.driver = driver
        self.empresa = empresa

    def verificar_palavras(self, palavras):
        lista = []
        for i, descricao in enumerate(self.descricoes):
            if any([True if s.lower() in descricao.lower() else False for s in palavras]):
                #output[len(output)] = [self.titulos[i], self.links[i], self.reclamacoes[i], self.descricoes[i], self.data[i].strftime('%d/%m/%Y')]
                lista.append([self.titulos[i], self.links[i], self.reclamacoes[i], self.descricoes[i], self.data[i].strftime('%d/%m/%Y')])
        return {self.empresa:lista}


    def extrair_informacoes(self, n_paginas):       

        tempo_maximo_espera = 30
        url = self.base_url + self.empresa + "/lista-reclamacoes/?pagina="
        self.reclamacoes, self.titulos, self.links = [], [], []

        for i in range(1, n_paginas + 1):
            self.driver.get(url + str(i))
            if i==1:
                sleep(5)
                cookie = self.driver.find_elements_by_id('onetrust-accept-btn-handler')
                if cookie:
                    cookie[0].click()
                
            WebDriverWait(self.driver, tempo_maximo_espera).until(EC.presence_of_element_located((By.CLASS_NAME, 'text-detail'))) 
            html = bs(self.driver.page_source, "html.parser")

            reclamacoes_html = html.find_all("p", {"class": "text-detail"})
            reclamacoes_na_pagina = [
                reclamacao.text.split("|") for reclamacao in reclamacoes_html
            ]
            self.reclamacoes.extend(reclamacoes_na_pagina)

            titulos_e_links = html.find_all(
                "a", {"class": "link-complain-id-complains"}
            )
            self.titulos.extend([titulo.text.strip() for titulo in titulos_e_links])
            self.links.extend([link.get("href") for link in titulos_e_links])

    def extrair_descricoes(self):

        tempo_maximo_espera = 30
        data_pattern = re.compile('\d\d/\d\d/\d\d')
        
        urls = [self.base_url + link[1:] for link in self.links]
        self.descricoes = []
        self.data = []
        #cont = 0

        for url in urls:
            self.driver.get(url)
            WebDriverWait(self.driver, tempo_maximo_espera).until(EC.presence_of_element_located((By.CLASS_NAME, 'complain-body'))) 
            registro = self.driver.find_elements_by_class_name('local-date')
            if registro:
                data = dt.datetime.strptime(data_pattern.search(registro[0].text).group(), '%d/%m/%y')
                self.data.append(data)
            else:
                self.data.append(None)
            html = bs(self.driver.page_source, "html.parser")
            descricao = html.find("div", {"class": "complain-body"}).text.strip()
            self.descricoes.append(descricao)
        
    def captura_reclamacao(self, area, nome, i):
        m = re.search('/.+/(.+)/$', nome)
        if m:
            arquivo = m.group(1)
        else:
            arquivo = 'captura_'+str(i)
            
        
        im = Image.open(io.BytesIO(self.driver.get_screenshot_as_png()))
        l = area.location
        s = area.size
        x = l['x']
        y = l['y']
        w = x + s['width']
        h = y + s['height']
        im = im.crop((x, y, w, h))
        im.save(arquivo+'.png')
