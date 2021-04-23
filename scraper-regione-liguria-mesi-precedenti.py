#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 12:36:51 2021

@author: matteomannini
"""
import locale
from datetime import datetime
import time
import requests
import re
from bs4 import BeautifulSoup
import json

locale.setlocale(locale.LC_TIME, "it_IT")


def request_and_make_the_soup(url):
    r = requests.get(url)
    print(r)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def extract_links(url):
    soup = request_and_make_the_soup(url)
    links = [a['href'] for a in soup.find('div', {'class', 'desc-content field_text'}).find_all('a', href=True)]
    return links


# extract tables with data and return a list object
def extract_tables():
    tables = []
    if data_r == '2021-03-25':
        for table in soup.find_all('table', {'style': 'width: 99%'}):
            tables.append(table)
        return tables
    else:
        for table in soup.find_all('table', {'style': 'width: 99%;'}):
            tables.append(table)
        return tables


# data report
def data_report():
    try:
        data_raw = soup.find('div', {'itemprop': "dateCreated"}).get_text(strip=True)
        regex = re.search(r"(\d\d) (\w+) (\d\d\d\d)", data_raw)
        data_raw_2 = regex.group(1) + '-' + regex.group(2) + '-' + regex.group(3)
        d = datetime.strptime(data_raw_2, '%d-%B-%Y')
        date: str = d.strftime('%Y-%m-%d')
        return date, d
    except:
        data_raw = soup.find('span', {'class': "fc_item_title"}).get_text(strip=True)
        regex = re.search(r"(\d+) (\w+) (\d\d\d\d)", data_raw)
        data_raw_2 = regex.group(1) + '-' + regex.group(2) + '-' + regex.group(3)
        d = datetime.strptime(data_raw_2, '%d-%B-%Y')
        date: str = d.strftime('%Y-%m-%d')
        return date, d


# tamponi

def extract_tamponi():
    table_zero_values = [cell.get_text(strip=True).replace('*', '') for cell in tables[0].find_all('p')]
    for value in table_zero_values:
        if table_zero_values.index(value) in [0, 3, 6, 9]:
            table_zero_values[table_zero_values.index(value)] = (value.replace(' ', '_'))
        else:
            table_zero_values[table_zero_values.index(value)] = int(value.replace('.', ''))
    tamponi = {}
    for i in range(0, 10, 3):
        tamponi[table_zero_values[i] + '_TOT'] = table_zero_values[i + 1]
        tamponi[table_zero_values[i] + '_PARZ'] = table_zero_values[i + 2]
    return tamponi


# CASI PER PROVINCIA DI RESIDENZA

def extract_casi_provincia():
    casi_provincia = {}
    table_1_values = [cell.get_text(strip=True) for cell in tables[1].find_all('p')]
    if 'SAVONA' in table_1_values[2]:
        for i in range(2, 13, 2):
            casi_provincia[table_1_values[i].replace(' ', '_')] = int(table_1_values[i + 1].replace('.', ''))
    else:
        for i in range(1, 12, 2):
            casi_provincia[table_1_values[i].replace(' ', '_')] = int(table_1_values[i + 1].replace('.', ''))
    return casi_provincia


# Ospedalizzati

def extract_ospedalizzati():
    ospedalizzati = {}
    table_2_values = [cell.get_text(strip=True) for cell in tables[2].find_all('td')]
    ospedalizzati['totali'] = {}
    for i in range(1, 4):
        ospedalizzati['totali'][table_2_values[i].replace(' ', '_')] = int(table_2_values[i + 4].replace('.', ''))

    for i in range(8, 77, 4):
        ospedalizzati[table_2_values[i].replace(' ', '_')] = {}
        ospedalizzati[table_2_values[i].replace(' ', '_')][table_2_values[1].replace(' ', '_')] = int(
            table_2_values[i + 1].replace('.', ''))
        ospedalizzati[table_2_values[i].replace(' ', '_')][table_2_values[2].replace(' ', '_')] = int(
            table_2_values[i + 2].replace('.', ''))
        ospedalizzati[table_2_values[i].replace(' ', '_')][table_2_values[3].replace(' ', '_')] = int(
            table_2_values[i + 3].replace('.', ''))
    return ospedalizzati


# Isolamento domiciliare - guariti - deceduti
def extract_isolamento_domiciliare_guariti_deceduti():
    isolamento_domiciliare = {}
    guariti = {}
    deceduti = {}

    table_3_values = [cell.get_text(strip=True) for cell in tables[3].find_all('p')]
    isolamento_domiciliare['totale'] = int(table_3_values[1].replace('.', ''))
    isolamento_domiciliare['parziale'] = int(table_3_values[2].replace('.', ''))
    guariti['totale'] = int(table_3_values[4].replace('.', ''))
    guariti['parziale'] = int(table_3_values[5].replace('.', ''))
    deceduti['totale'] = int(table_3_values[7].replace('.', ''))
    deceduti['parziale'] = int(table_3_values[8].replace('.', ''))
    return isolamento_domiciliare, guariti, deceduti


# dettaglio deceduti
def extract_dettaglio_deceduti():
    dettaglio_deceduti = {}
    table_4_values = [cell.get_text(strip=True) for cell in tables[4].find_all('td')]
    if 'decesso' in table_4_values[0]:
        for i in range(1, deceduti['parziale'] + 1):
            dettaglio_deceduti[i] = {}
            dettaglio_deceduti[i]['Data_decesso'] = table_4_values[i * 4].replace(' ', '_')
            dettaglio_deceduti[i]['Sesso'] = table_4_values[(i * 4) + 1].replace(' ', '_')
            dettaglio_deceduti[i]['Età'] = int(table_4_values[(i * 4) + 2].replace('.', ''))
            dettaglio_deceduti[i]['Luogo_decesso'] = table_4_values[(i * 4) + 3].replace(' ', '_')
    elif '1' in table_4_values[0]:
        for i in range(0, deceduti['parziale']):
            dettaglio_deceduti[i + 1] = {}
            dettaglio_deceduti[i + 1]['Data_decesso'] = table_4_values[(i * 5) + 1].replace(' ', '_')
            dettaglio_deceduti[i + 1]['Sesso'] = table_4_values[(i * 5) + 2].replace(' ', '_')
            dettaglio_deceduti[i + 1]['Età'] = int(table_4_values[(i * 5) + 3].replace('.', ''))
            dettaglio_deceduti[i + 1]['Luogo_decesso'] = table_4_values[(i * 5) + 4].replace(' ', '_')
    else:
        for i in range(1, deceduti['parziale'] + 1):
            dettaglio_deceduti[i] = {}
            dettaglio_deceduti[i]['Data_decesso'] = table_4_values[(i * 5) + 1].replace(' ', '_')
            dettaglio_deceduti[i]['Sesso'] = table_4_values[(i * 5) + 2].replace(' ', '_')
            dettaglio_deceduti[i]['Età'] = int(table_4_values[(i * 5) + 3].replace('.', ''))
            dettaglio_deceduti[i]['Luogo_decesso'] = table_4_values[(i * 5) + 4].replace(' ', '_')
    return dettaglio_deceduti


# sorveglianze attive
def extract_sorveglianze_attive():
    sorveglianze_attive = {}
    if data_r == '2021-03-06':
        table_4_values = [cell.get_text(strip=True) for cell in tables[4].find_all('td')]
        sorveglianze_attive['ASL_1'] = int(table_4_values[39].replace('.', ''))
        sorveglianze_attive['ASL_2'] = int(table_4_values[42].replace('.', ''))
        sorveglianze_attive['ASL_3'] = int(table_4_values[45].replace('.', ''))
        sorveglianze_attive['ASL_4'] = int(table_4_values[48].replace('.', ''))
        sorveglianze_attive['ASL_5'] = int(table_4_values[51].replace('.', ''))
        sorveglianze_attive['Liguria'] = int(table_4_values[54].replace('.', ''))
    else:
        table_5_values = [cell.get_text(strip=True) for cell in tables[5].find_all('p')]
        for i in range(2, 13, 2):
            sorveglianze_attive[table_5_values[i].replace(' ', '_')] = int(table_5_values[i + 1].replace('.', ''))


url = 'https://www.regione.liguria.it/homepage/salute-e-sociale/homepage-coronavirus/bollettino-coronavirus/dati-marzo-2021.html'
links = extract_links(url)
data_cambio_formato = datetime(2021, 1, 15)

for link in links:
    time.sleep(5)
    soup = request_and_make_the_soup(link)
    data_r, data_dt = data_report()
    tables = extract_tables()
    if data_dt > data_cambio_formato:
        print(f"{data_r} ready to parse")
        tamponi = extract_tamponi()
        casi_provincia = extract_casi_provincia()
        ospedalizzati = extract_ospedalizzati()
        isolamento_domiciliare, guariti, deceduti = extract_isolamento_domiciliare_guariti_deceduti()
        dettaglio_deceduti = extract_dettaglio_deceduti()
        sorveglianze_attive = extract_sorveglianze_attive()
        report = {
            'date': data_r,
            'link': link,
            'tamponi': tamponi,
            'casi_provincia': casi_provincia,
            'ospedalizzati': ospedalizzati,
            'isolamento_domiciliare': isolamento_domiciliare,
            'guariti': guariti,
            'deceduti': deceduti,
            'dettaglio_deceduti': dettaglio_deceduti,
            'sorveglianze_attive': sorveglianze_attive
        }

        with open(data_r + '.json', 'w') as outfile:
            json.dump(report, outfile)
            print(f"wrote {data_r} report")

    else:
        print(f"skipping {data_r}")
