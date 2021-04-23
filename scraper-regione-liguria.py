#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 12:36:51 2021

@author: matteomannini
"""
import locale
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup
import json

locale.setlocale(locale.LC_TIME, "it_IT")

day = 21
url = f'https://www.regione.liguria.it/homepage/salute-e-sociale/homepage-coronavirus/bollettino-coronavirus/dati-{day}-4-2021.html'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

tables = []
for table in soup.find_all('table', {'style': 'width: 99%;'}):
    tables.append(table)


# data report
def data_report():
    data_raw = soup.find('div', {'itemprop': "dateCreated"}).get_text(strip=True)
    regex = re.search(r"(\d\d) (\w+) (\d\d\d\d)", data_raw)
    data_raw_2 = regex.group(1) + '-' + regex.group(2) + '-' + regex.group(3)
    d = datetime.strptime(data_raw_2, '%d-%B-%Y')
    date: str = d.strftime('%Y-%m-%d')
    return date


data_r = data_report()

# tamponi

table_zero_values = [cell.get_text(strip=True) for cell in tables[0].find_all('p')]

for value in table_zero_values:
    if table_zero_values.index(value) in [0, 3, 6, 9]:
        table_zero_values[table_zero_values.index(value)] = (value.replace(' ', '_'))
    else:
        table_zero_values[table_zero_values.index(value)] = int(value.replace('.', ''))

tamponi = {}

for i in range(0, 10, 3):
    tamponi[table_zero_values[i] + '_TOT'] = table_zero_values[i + 1]
    tamponi[table_zero_values[i] + '_PARZ'] = table_zero_values[i + 2]

# CASI PER PROVINCIA DI RESIDENZA

casi_provincia = {}
table_1_values = [cell.get_text(strip=True) for cell in tables[1].find_all('p')]
if 'SAVONA' in table_1_values[2]:
    for i in range(2, 13, 2):
        casi_provincia[table_1_values[i].replace(' ', '_')] = int(table_1_values[i + 1].replace('.', ''))
else:
    for i in range(1, 12, 2):
        casi_provincia[table_1_values[i].replace(' ', '_')] = int(table_1_values[i + 1].replace('.', ''))

# Ospedalizzati

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

# Isolamento domiciliare - guariti - deceduti

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

# dettaglio deceduti

dettaglio_deceduti = {}
table_4_values = [cell.get_text(strip=True) for cell in tables[4].find_all('td')]
if data_r == '2021-04-18':
    for i in range(1, deceduti['parziale'] + 1):
        dettaglio_deceduti[i] = {}
        dettaglio_deceduti[i][table_4_values[0].replace(' ', '_')] = table_4_values[i * 4].replace(' ', '_')
        dettaglio_deceduti[i][table_4_values[1].replace(' ', '_')] = table_4_values[(i * 4) + 1].replace(' ', '_')
        dettaglio_deceduti[i][table_4_values[2].replace(' ', '_')] = int(table_4_values[(i * 4) + 2].replace('.', ''))
        dettaglio_deceduti[i][table_4_values[3].replace(' ', '_')] = table_4_values[(i * 4) + 3].replace(' ', '_')
else:
    for i in range(1, deceduti['parziale'] + 1):
        dettaglio_deceduti[i] = {}
        dettaglio_deceduti[i][table_4_values[1].replace(' ', '_')] = table_4_values[(i * 5)+1].replace(' ', '_')
        dettaglio_deceduti[i][table_4_values[2].replace(' ', '_')] = table_4_values[(i * 5) + 2].replace(' ', '_')
        dettaglio_deceduti[i][table_4_values[3].replace(' ', '_')] = int(table_4_values[(i * 5) + 3].replace('.', ''))
        dettaglio_deceduti[i][table_4_values[4].replace(' ', '_')] = table_4_values[(i * 5) + 4].replace(' ', '_')
# sorveglianze attive

sorveglianze_attive = {}
table_5_values = [cell.get_text(strip=True) for cell in tables[5].find_all('p')]
for i in range(2, 13, 2):
    sorveglianze_attive[table_5_values[i].replace(' ', '_')] = int(table_5_values[i + 1].replace('.', ''))

report = {
    'date': data_r,
    'link': url,
    'tamponi': tamponi,
    'casi_provincia': casi_provincia,
    'ospedalizzati': ospedalizzati,
    'isolamento_domiciliare': isolamento_domiciliare,
    'guariti': guariti,
    'deceduti': deceduti,
    'dettaglio_deceduti': dettaglio_deceduti,
    'sorveglianze_attive': sorveglianze_attive
}

with open(data_r+'.json', 'w') as outfile:
    json.dump(report, outfile)