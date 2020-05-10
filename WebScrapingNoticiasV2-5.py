# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 19:08:59 2020

@author: Lucas E. La Pietra

Changes:Agregados delays para evitar multiples instancias de webdrivers, lo que causa el error 10054
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import nltk
import time

driver = webdriver.Chrome("D:/Users/User/Documents/PS/chromedriver")
nltk.download('punkt')

def infobae(driver):
    titulos=[] 
    html=[]
    corpus=[]
    diario=[]
    fechas=[]
    categorias=[]
    cuerpo=''
    driver.get("https://www.infobae.com/coronavirus")
    url='https://www.infobae.com'
    content = driver.page_source
    soup = BeautifulSoup(content,features="lxml")
    time.sleep(3)
    for a in soup.findAll('div', attrs={'class':'headline normal normal-style'}):
        for b in a.findAll('a'):                     
            html.append(url+b['href']) 
    html = list(dict.fromkeys(html))
    for link in html:
        time.sleep(3)
        driver.get(link)
        content = driver.page_source
        soup = BeautifulSoup(content,features="lxml")
        time.sleep(4)
        titulo=soup.find('h1')
        titulos.append(titulo.text)
        for a in soup.findAll('p', attrs={'class':'element element-paragraph'}):
            cuerpo+=a.text
        for a in soup.findAll('p', attrs={'class':'font_tertiary paragraph'}):
            cuerpo+=a.text
        categoria=soup.find('div', attrs={'class':'header-label'})
        categorias.append(categoria.text)
        corpus.append(cuerpo)
        diario.append('Infobae')
        fechas.append(datetime.date.today().strftime("%d/%m/%Y"))
        cuerpo=''
    df = pd.DataFrame({'Titulo':titulos,'Link':html,'Corpus':corpus,'Categoria':categorias,'Diario':diario,'Fecha':fechas})
    return df

def lanacion(driver): 
    titulos=[] 
    html=[]
    corpus=[]
    diario=[]
    fechas=[]
    categorias=[]
    cuerpo=''
    driver.get("https://www.lanacion.com.ar/tema/coronavirus-tid67578")
    url='https://www.lanacion.com.ar'
    content = driver.page_source
    soup = BeautifulSoup(content,features="lxml")
    time.sleep(3)
    columnanoticias=soup.find('section', attrs={'class':'cuerpo'})
    for a in columnanoticias.findAll('article', attrs={'class':'nota'}, limit=15):
        for b in a.findAll('a', attrs={'class':'figure'}):                                 
            html.append(url+b['href'])  
    html = list(dict.fromkeys(html))
    for link in html:
        time.sleep(3)
        driver.get(link)
        content = driver.page_source
        soup = BeautifulSoup(content,features="lxml")
        time.sleep(4)
        titulo=soup.find('h1')
        titulos.append(titulo.text)
        categoria=soup.find('strong', attrs={'class':'categoria'})
        if categoria is not None:
            categorias.append(categoria.text.strip())
        else:
            categorias.append('Coronavirus')
        newsbody=soup.find('section', attrs={'id':'cuerpo'})
        for a in newsbody.findAll('p'):
            if "Columnistas" in a.text: break
            cuerpo+=a.text
        corpus.append(cuerpo)
        diario.append('La Nacion')
        fechas.append(datetime.date.today().strftime("%d/%m/%Y"))        
        cuerpo=''        
    df = pd.DataFrame({'Titulo':titulos,'Link':html,'Corpus':corpus,'Categoria':categorias,'Diario':diario,'Fecha':fechas})
    return df

def clarin(driver):
    titulos=[] 
    html=[]
    corpus=[]
    diario=[]
    fechas=[]
    categorias=[]
    cuerpo=''
    driver.get("https://www.clarin.com/coronavirus")
    url='https://www.clarin.com'
    content = driver.page_source
    soup = BeautifulSoup(content,features="lxml")
    time.sleep(3)
    for a in soup.findAll('article', attrs={'class':'content-nota onexone_foto list NWS'}):
        b=a.find('a')                     
        html.append(url+b['href'])      
    html = list(dict.fromkeys(html))
    for link in html:
        time.sleep(3)
        driver.get(link)
        content = driver.page_source
        soup = BeautifulSoup(content,features="lxml")
        time.sleep(1)
        titulo=soup.find('h1', attrs={'id':'title'})
        titulos.append(titulo.text)
        categoria=soup.find('a', attrs={'class':'subhome-name'})
        categorias.append(categoria.text)
        newsbody=soup.find('div', attrs={'class':'body-nota'})
        for a in newsbody.findAll('p'):     
            if "COMENTARIOS" in a.text: break
            cuerpo+=a.text
        corpus.append(cuerpo)
        diario.append('Clarin')
        fechas.append(datetime.date.today().strftime("%d/%m/%Y"))
        cuerpo=''
    df = pd.DataFrame({'Titulo':titulos,'Link':html,'Corpus':corpus,'Categoria':categorias,'Diario':diario,'Fecha':fechas})
    return df


dfinfobae=infobae(driver)
dflanacion=lanacion(driver)
dfclarin=clarin(driver)
df=pd.concat([dfinfobae,dflanacion,dfclarin])

hoy=datetime.date.today().strftime("%d-%m-%Y")
ruta="D:/Users/User/Documents/PS/BDNoticias-%s.xlsx"%(hoy)
df.to_excel(ruta, index = False)