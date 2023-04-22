from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool, Column, Div, Row, Div, Paragraph, NumeralTickFormatter
import pandas as pd
from bokeh.palettes import Set1
from bokeh.layouts import column, row
from pandas import DataFrame
import numpy as np
import json
from pprint import pprint

def import_data(file_list):
    df_list = []
    for filepath in file_list:
        with open(filepath, "r", encoding="utf-8") as fp:
            df = pd.read_json(fp)
            df_list.append(df)
    return df_list



croisieres = import_data(["trafic-croisieres-region-bretagne.json"])[0]

croisieres_by_year = croisieres.groupby([pd.Grouper(key='date', freq='Y'), 'nom_du_port']).sum()
pprint(type(croisieres_by_year))

pprint(croisieres_by_year.head())

pprint(croisieres_by_year.index)

croisieres_by_year.reset_index(inplace = True)

pprint(croisieres_by_year.head())

croisieres_brest = croisieres_by_year[croisieres_by_year["nom_du_port"] == 'BREST']
croisieres_stmalo = croisieres_by_year[croisieres_by_year["nom_du_port"] == 'SAINT-MALO']
croisieres_lorient = croisieres_by_year[croisieres_by_year["nom_du_port"] == 'LORIENT']
croisieres_brest = croisieres_brest.drop("nom_du_port", axis = 1)
croisieres_stmalo = croisieres_stmalo.drop("nom_du_port", axis = 1 )
croisieres_lorient = croisieres_lorient.drop("nom_du_port", axis = 1)
pprint(croisieres_brest.head())

croisieres_by_year = pd.merge(croisieres_brest,croisieres_stmalo, on = 'date', suffixes=("_brest", "_stmalo"))
croisieres_by_year = pd.merge(croisieres_by_year,croisieres_lorient, on = 'date')
croisieres_by_year = croisieres_by_year.rename(columns={"nombre_de_passagers_brest": "BREST", "nombre_de_passagers_stmalo": "SAINT-MALO", "nombre_de_passagers": "LORIENT"})
croisieres_by_year["date"] = croisieres_by_year["date"].apply(lambda x: str(x.year))
pprint(croisieres_by_year.head())


source = ColumnDataSource(croisieres_by_year)

ports = list(croisieres_by_year.columns[1:4])
years = [date for date in croisieres_by_year["date"]]

p = figure(y_range = croisieres_by_year["date"],height=250, title="Nombre de passagers de croisière par an en fonction du port",
           toolbar_location=None, tools="hover", tooltips="$name @date: @$name")
palette = ('#1B998B', '#3B1C32', '#CA054D')
p.hbar_stack(ports,y = 'date', source = source, legend_label=ports, width=0.9, color=palette)

show(p)