from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool, Column, Div, Row, Div, Paragraph
import pandas as pd
from bokeh.palettes import Set1
from bokeh.layouts import column, row
from pandas import DataFrame
import numpy as np
import json

def import_data(file_list):
    df_list = []
    for filepath in file_list:
        with open(filepath, "r", encoding="utf-8") as fp:
            df = pd.read_json(fp)
            df_list.append(df)
    return df_list



ferries = import_data(["trafic-ferries-bretagne.json"])[0]


ferries_roscoff = ferries[ferries["code_du_port"] == "FRROS"]
ferries_stmalo = ferries[ferries["code_du_port"] == "FRSML"]
ferries_roscoff = ferries_roscoff.sort_values(by="date")
ferries_stmalo = ferries_stmalo.sort_values(by="date")

ferries_stmalo["date"].dtype

print(ferries_roscoff.head())
print(ferries_stmalo.head())

source1 = ColumnDataSource(ferries_roscoff)
source2 = ColumnDataSource(ferries_stmalo)

hovertool = HoverTool(
    tooltips = [('Port', '@nom_du_port'),
                ('Nombre de passagers', '@nombre_de_passagers'),
                ('Date', '@date{%m/%y}')],
    
    formatters = {
        '@date' : 'datetime'
    }
)

p = figure(width=1200, 
           height=400, 
           title="Titre",
           x_axis_type = "datetime",
           background_fill_color = "#00100B") 

p.line(x = "date", 
       y = "nombre_de_passagers",
       source = source1,
       color = "green",
       line_width = 3,
       legend_label = 'Roscoff')

p.circle(x = "date", 
         y = "nombre_de_passagers", 
         source = source1,
         fill_color="#00100B", 
         color = "green",
         size=8)

p.line(x = "date", 
       y = "nombre_de_passagers",
       source = source2,
       color = "purple",
       line_width = 3,
       legend_label = 'Saint-Malo')

p.circle(x = "date", 
         y = "nombre_de_passagers", 
         source = source2,
         fill_color="#00100B", 
         color = "purple",
         size=8)


p.add_tools(hovertool)

show(p)
