from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool, Column, Div, Row, Div, Paragraph
import pandas as pd
from bokeh.palettes import Set1
from bokeh.layouts import column, row
from pandas import DataFrame
import numpy as np
import json
from bokeh.models import Tabs, TabPanel
from bokeh.models import ColorPicker, Spinner
from bokeh.models import CustomJS

#################### Importation des données ####################################
 
with open("lignes-routieres-departementales-gerees-par-la-region-bretagne.json", 'r', encoding = 'utf-8') as fp:
    breizh_go = json.load(fp)

with open("arrets-ferroviaires-regionaux-de-la-region-bretagne.json", 'r', encoding = "utf-8") as fp2:
    gares_bretagne = json.load(fp2)

#################### Définition de fonctions ###################################

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


#################### Appel de fonctions ###################################

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


####################### Représentations #####################################

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


####################### Mise en page #####################################

# Premier onglet
div = Div(text="""
<h1> Les transports dans la région Bretagne </h1>
<p> Nous avons voulu représenter (de manière non exhaustive) les différents moyens de transport que l'on peut emprunter au sein de la Région Bretagne. Vous pouvez trouver les bases de données utilisées aux adresses suivantes : </p>
<ul><li><a href="https://data.bretagne.bzh/explore/dataset/lignes-routieres-departementales-gerees-par-la-region-bretagne/information/?location=8,48.23199,-2.73834&basemap=jawg.streets ">Lignes routières du réseau BreizhGo</a></li>
<li><a href="https://data.bretagne.bzh/explore/dataset/arrets-ferroviaires-regionaux-de-la-region-bretagne/map/?location=8,48.0634,-2.67242&basemap=jawg.streets ">Gares du réseau ferroviaire</a><l/i>
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

# Construction des onglets

tab1 = TabPanel(child=layout, title="Réseau BreizhGo")
tab2 = TabPanel(child=layout2, title="Gares de Bretagne")
tabs = Tabs(tabs = [tab1, tab2])

#Sortie
show(tabs)