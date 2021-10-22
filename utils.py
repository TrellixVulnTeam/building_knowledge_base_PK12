import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
import requests

import re
import lxml
from unicodedata import normalize

# Info about depo, transaction, loan and card
def product_info(linkie, product):
    html_text = requests.get(linkie).text
    soup = BeautifulSoup(html_text, 'lxml')
    
    # Content section includes product name, summary and 2 optional fields
    content = soup.find('div', class_ = 'cart-content uk-width-1-1 uk-width-expand@m')
    all_div_in_content = content.find_all('div')
    
    # About product
    product_name = content.h2.text
    about_product = all_div_in_content[0].text.strip()
    
    # Бүрдүүлэх материалууд
    required_materials = soup.find_all('div', class_ = 'gt-element gt-table')[-1]
    required_materials = re.sub('[\n]+', '\n', required_materials.text.strip()).split('\n')    
    
    # For storing additional informations
    # Веб сайт дээр бүтээгдэхүүний нэр болон тайлбарын доод хэсэгт байдаг мэдээллүүд
    temp_1 = []
    temp_2 = []
    
    # Tables
    tables = soup.find_all('table')
    dfs = []
    """
    cleaned_tables = []

    for table in tables:
        temp_table = normalize('NFKD', table.text.strip()).split('\n\n\n')
        temp_table = [re.sub('[\n]+', '\n', item.strip()).split('\n') for item in temp_table]
        cleaned_tables.append(temp_table)""" # Needs some work
    
    for table in tables:
        df = normalize('NFKD', table.text.strip())
        df = pd.read_html(str(table))[0]
        df = df.dropna(axis = 1, how = 'all')
        df.columns = ['col_'+str(i+1) for i in range(df.shape[1])]
        # '-' here is in some other format 
        df = df.replace(['–'], '-')
        dfs.append(df)

    if len(all_div_in_content) > 1:
        if product == 'depo':
            # Веб сайт дээр бүтээгдэхүүний нэр болон тайлбарын доод хэсэгт байдаг мэдээллүүд
            yearly_interest = all_div_in_content[1].span.text + ': ' + all_div_in_content[2].div.text
            temp_1 = yearly_interest
    
        elif product == 'loan':
            time_and_max_amount = all_div_in_content[1].find_all('div', class_ = "card-meta-item")

            if len(time_and_max_amount) > 1:
                time_limit = time_and_max_amount[0].span.text + ': ' + time_and_max_amount[0].div.text
                max_amount = time_and_max_amount[1].span.text + ': ' + time_and_max_amount[1].div.text
            else:
                time_limit = time_and_max_amount[0].span.text + ': ' + time_and_max_amount[0].div.text
                max_amount = []

            temp_1 = time_limit
            temp_2 = max_amount
            
        elif product == 'card':
            time_and_currency = all_div_in_content[1].find_all('div', class_ = "card-meta-item")
            
            if len(time_and_currency) > 1:
                time_limit = time_and_currency[0].span.text + ': ' + time_and_currency[0].div.text
                currency = time_and_currency[1].span.text + ': ' + time_and_currency[1].div.text
            else:
                time_limit = time_and_currency[0].span.text + ': ' + time_and_currency[0].div.text
                currency = []
            
            # Бүрдүүлэх материал
            required_materials = soup.find_all('div', class_ = 'gt-element gt-table')
            
            if len(required_materials) > 1:
                # Required materials. The order of items on the web was different from others
                required_materials = required_materials[1]
                required_materials = re.sub('[\n]+', '\n', required_materials.text.strip()).split('\n')  
            else:
                required_materials = []

            temp_1 = time_limit
            temp_2 = currency
    else:
        if product == 'account':
            pass
    
    return product_name, about_product, temp_1, temp_2, required_materials, dfs
