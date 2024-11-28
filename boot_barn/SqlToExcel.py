import os

import pandas as pd
import pymysql
import db_config

# # Creating a connection to SQL Database
connection = pymysql.connect(host='localhost', user='root', database='storeLocator', password='actowiz', charset='utf8mb4', autocommit=True)

table_name = 'boot_barn_27_11_2024'

fetch_query = f'''SELECT * FROM {table_name};'''  # Query that will retrieve all data from Database table

# excel_path = r"C:\Users\jaimin.gurjar\Downloads"
excel_path = rf"C:\Project Files Live (using Scrapy)\storeLocator\{db_config.delivery_date}"
os.makedirs(name=excel_path, exist_ok=True)

# Create Excel file form SQL data
# dataframe = pd.read_sql(sql=fetch_query, con=connection).drop(columns='index_id')
dataframe = pd.read_sql(sql=fetch_query, con=connection)

filename = table_name + '_states' + '.xlsx'
writer = pd.ExcelWriter(
    path=excel_path + fr"\{filename}",
    engine='xlsxwriter',
    engine_kwargs={'options': {'strings_to_urls': False}}
)
dataframe.to_excel(excel_writer=writer, index=False)

# dataframe.to_excel(writer)
writer.close()
