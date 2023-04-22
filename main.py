from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool, Column, Div, Row, Div, Paragraph, NumeralTickFormatter
from bokeh.models import Tabs, TabPanel
import pandas as pd
from bokeh.palettes import Set1
from bokeh.layouts import column, row
from bokeh.models import ColorPicker, Spinner
from bokeh.models import CustomJS
from pandas import DataFrame
import numpy as np
from pprint import pprint
import json


## Définition des fonctions

def import_data(file_list):
    df_list = []
    for filepath in file_list:
        with open(filepath, "r", encoding="utf-8") as fp:
            df = pd.read_json(fp)
            df_list.append(df)
    return df_list

### Fonction de conversion en format Mercator

def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)


### Fonction pour récupérer les données des lignes breizhgo

def analyse_data(data):
    # Construction d'un dataframe 
    nom_ligne = []
    saison = []
    coordsx = []  # Pour chaque zone, liste des coordonnées x de la polyligne
    coordsy = []  # Pour chaque zone, liste des coordonnées y de la polyligne

    for ligne in data:
        nom_ligne.append(ligne["nom"])
        saison.append(ligne["saison"])
        coords = ligne["geo_shape"]["geometry"]["coordinates"]
        c_x=[]
        c_y=[]
        for c in coords[0] :
            x,y = coor_wgs84_to_web_mercator(c[0],c[1])
            c_x.append(x)
            c_y.append(y)
        coordsx.append(c_x)
        coordsy.append(c_y)

    df = DataFrame({'nom_ligne': nom_ligne, 'saison': saison, 'x':coordsx,'y':coordsy})
    return df


### Fonction pour récupérer les données des gares

def analyse_data2(data):
    # Construction d'un dataframe 
    nom_gare = []
    ville = []
    coordsx = []  
    coordsy = []  

    for gare in data:
        nom_gare.append(gare["nom"])
        ville.append(gare["commune"])
        coords = gare["geo_point_2d"]
        x,y = coor_wgs84_to_web_mercator(coords["lon"], coords["lat"])
        coordsx.append(x)
        coordsy.append(y)

    df = DataFrame({'nom_gare': nom_gare, 'ville': ville, 'x':coordsx,'y':coordsy})
    return df

## Cartes ## 

with open("lignes-routieres-departementales-gerees-par-la-region-bretagne.json", 'r', encoding = 'utf-8') as fp:
    breizh_go = json.load(fp)

with open("arrets-ferroviaires-regionaux-de-la-region-bretagne.json", 'r', encoding = "utf-8") as fp2:
    gares_bretagne = json.load(fp2)

data = analyse_data(breizh_go)
print(data.iloc[0])


couleur = DataFrame([{'saison':"annuelle", 'couleur':"red"},
                     {'saison':"scolaire", 'couleur':"orange"},
                     {'saison':"été", 'couleur':"yellow"}, 
                     {'saison':"hors été", 'couleur':"brown"}])

data = data.merge(couleur, left_on = "saison", right_on = "saison")
# print(data.iloc[0])

donnees = analyse_data2(gares_bretagne)
# print(donnees.iloc[0])


# On convertit en ColumnDataSource
source = ColumnDataSource(data)
source2 = ColumnDataSource(donnees)

#### On crée la carte des lignes bzeizhGo avec fond de carte
p = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Lignes du réseau Breizh Go", toolbar_location="below")
p.add_tile("OSM")
p.title.text_color='brown'

p.multi_line(xs = "x", ys = "y", source = source, color = "couleur", line_width = 3)
hover_tool = HoverTool(tooltips=[( 'Nom de la ligne', '@nom_ligne'), ( 'Type de ligne', '@saison')]) # outil d'affichage au survol : nom de la ligne
p.add_tools(hover_tool)


#### On crée la carte des gares de Bretagne avec fond de carte
carte = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Gares de la région Bretagne", toolbar_location="below")
carte.add_tile("OSM")
carte.title.text_color='brown'

picker1 = ColorPicker(title = "Couleur des points", color = "red") # choix de la couleur des points

# Points sur la carte
cercles = carte.circle(x = "x", y = "y", source = source2, size = 5, fill_color = "red", line_color='black')

callback = CustomJS(args=dict(cercles =cercles, picker1=picker1), code="""
    cercles.glyph.fill_color = picker1.color;
""")

picker1.js_on_change('color', callback)

# Outil de survol qui affiche le nom de la gare et la commune
hover_tool2 = HoverTool(tooltips=[( 'Nom de la gare', '@nom_gare'),( 'Commune', '@ville')])
carte.add_tools(hover_tool2)


## Plot des croisières 

croisieres = import_data(["trafic-croisieres-region-bretagne.json"])[0]

croisieres_by_year = croisieres.groupby([pd.Grouper(key='date', freq='Y'), 'nom_du_port']).sum()

croisieres_by_year.reset_index(inplace = True)



croisieres_brest = croisieres_by_year[croisieres_by_year["nom_du_port"] == 'BREST']
croisieres_stmalo = croisieres_by_year[croisieres_by_year["nom_du_port"] == 'SAINT-MALO']
croisieres_lorient = croisieres_by_year[croisieres_by_year["nom_du_port"] == 'LORIENT']
croisieres_brest = croisieres_brest.drop("nom_du_port", axis = 1)
croisieres_stmalo = croisieres_stmalo.drop("nom_du_port", axis = 1 )
croisieres_lorient = croisieres_lorient.drop("nom_du_port", axis = 1)


croisieres_by_year = pd.merge(croisieres_brest,croisieres_stmalo, on = 'date', suffixes=("_brest", "_stmalo"))
croisieres_by_year = pd.merge(croisieres_by_year,croisieres_lorient, on = 'date')
croisieres_by_year = croisieres_by_year.rename(columns={"nombre_de_passagers_brest": "BREST", "nombre_de_passagers_stmalo": "SAINT-MALO", "nombre_de_passagers": "LORIENT"})
croisieres_by_year["date"] = croisieres_by_year["date"].apply(lambda x: str(x.year))



source = ColumnDataSource(croisieres_by_year)

ports = list(croisieres_by_year.columns[1:4])
years = [date for date in croisieres_by_year["date"]]

p3 = figure(y_range = croisieres_by_year["date"], title="Nombre de passagers de croisière par année",
           toolbar_location=None, tools="hover", tooltips="$name @date: @$name", background_fill_color = "#EDE8E9")
palette = ('#1B998B', '#3B1C32', '#CA054D')
p3.hbar_stack(ports,y = 'date', source = source, legend_label=ports,height = 0.9 , color=palette)

p3.xaxis[0].formatter = NumeralTickFormatter(format="0.")
p3.x_range.start = 0
p3.y_range.range_padding = 0.1
p3.axis.minor_tick_line_color = None

## Plot des ferries

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

p2 = figure(width=1200, 
           height=400, 
           title="Nombre de passagers dans les ports de Saint-Malo et Roscoff par mois",
           x_axis_type = "datetime",
           background_fill_color = "#EDE8E9") 

p2.yaxis[0].formatter = NumeralTickFormatter(format="0.")

p2.line(x = "date", 
       y = "nombre_de_passagers",
       source = source1,
       color = "#CA054D",
       line_width = 3,
       legend_label = 'Roscoff')

p2.circle(x = "date", 
         y = "nombre_de_passagers", 
         source = source1,
         fill_color="#EDE8E9", 
         color = "#CA054D",
         size=8)

p2.line(x = "date", 
       y = "nombre_de_passagers",
       source = source2,
       color = "#3B1C32",
       line_width = 3,
       legend_label = 'Saint-Malo')

p2.circle(x = "date", 
         y = "nombre_de_passagers", 
         source = source2,
         fill_color="#EDE8E9", 
         color = "#3B1C32",
         size=8)


p2.add_tools(hovertool)

####################### Mise en page #####################################

# Premier onglet
div = Div(text="""
<h1> Les transports dans la région Bretagne </h1>
<p> Nous avons voulu représenter (de manière non exhaustive) les différents moyens de transport que l'on peut emprunter au sein de la Région Bretagne. Vous pouvez trouver les bases de données utilisées aux adresses suivantes : </p>
<ul><li><a href="https://data.bretagne.bzh/explore/dataset/lignes-routieres-departementales-gerees-par-la-region-bretagne/information/?location=8,48.23199,-2.73834&basemap=jawg.streets ">Lignes routières du réseau BreizhGo</a></li>
<li><a href="https://data.bretagne.bzh/explore/dataset/arrets-ferroviaires-regionaux-de-la-region-bretagne/map/?location=8,48.0634,-2.67242&basemap=jawg.streets ">Gares du réseau ferroviaire</a><l/i>
<li><a href="https://data.bretagne.bzh/explore/dataset/trafic-ferries-region-bretagne/table/">Trafic ferries Région Bretagne</a><l/i>
<li><a href="https://data.bretagne.bzh/explore/dataset/trafic-croisieres-region-bretagne/table/">Trafic croisières Région Bretagne</a><l/i>
</ul>""")


par = Paragraph(text = "Indications pour ce premier graphique : n'hésitez pas à passer votre souris pour afficher le nom des lignes !")

# Deuxième onglet
img = Div(text="""<img src="gare_rennes.jpg" width="400"/>
""")
comment = Paragraph(text="Illustration : la gare de Rennes")

# layout = Column(titre,Row(p,data_table,(Column (comment,img))),Row(p2,comment2))

# Construction des layout pour chacun des onglets
layout = row(p, column (div, par))
layout2 = row(carte, column (picker1, img, comment))
layout3 = row(p3)
layout4 = row(p2)

# Construction des onglets

tab1 = TabPanel(child=layout, title="Réseau BreizhGo")
tab2 = TabPanel(child=layout2, title="Gares de Bretagne")
tab3 = TabPanel(child =layout3, title="Trafic croisières Région Bretagne")
tab4 = TabPanel(child=layout4, title="Trafic ferries Région Bretagne")
tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])

#Sortie
show(tabs)