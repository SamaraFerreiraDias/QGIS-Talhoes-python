#Obs: selecionar somente o layer "Linhas_De_Cana"
from qgis.core import *
from qgis.gui import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math 

#Funcoes========================================================================
def novaLinha(linhasTotais, linhasAtend):
    new_list = []
    for i in range(0, len(linhasTotais), linhasAtend):
        subset = linhasTotais[i:i+linhasAtend]
        x = sum(p.x() for p in subset) / linhasAtend
        y = sum(p.y() for p in subset) / linhasAtend
        new_list.append(QgsPointXY(x, y))
    return new_list
       

#===============================================================================
mapCanvas = iface.mapCanvas()
n = mapCanvas.layerCount()
layer = [mapCanvas.layer(i) for i in range(n)]
layer = layer[0]

#ler linhas
#ordenar pelo campo FID
features = []
features = sorted(layer.getFeatures(), key=lambda x: x['fid'])

#ler lista de linhas e inverter ordem dos vertices nas linhas impares
linhasTotais = []
i = 0
for feat in features:
    geom = feat.geometry()
    #print feat['fid']
    if geom.type() == QgsWkbTypes.LineGeometry:
        linhas = geom.asMultiPolyline()
        for linha in linhas:
            if (i % 2) != 0:
                linha.reverse()
            linhasTotais += linha
            i += 1

linhasTotais.reverse() #para retirar do final

# Gerar linhas
step, confirm = QInputDialog.getInt(None, "Qgis" ,"Quantas linhas a máquina atende por vez? ")

if confirm:
    intermediate_points = novaLinha(linhasTotais, step)

    # Criar camada vazia para armazenar as linhas
    layer = QgsVectorLayer("LineString", "Rota_Intermediaria", "memory")
    crs = layer.crs()
    crs.createFromId(31982)
    layer.setCrs(crs)
        
    # Adicionar a camada ao projeto
    QgsProject.instance().addMapLayer(layer)

    # Criar objetos QgsFeature e adicionar à camada
    features = [QgsFeature() for _ in range(len(intermediate_points))]
    for i, feature in enumerate(features):
        geometry = QgsGeometry.fromPolylineXY(intermediate_points[i*step:(i+1)*step])
        feature.setGeometry(geometry)
    layer.dataProvider().addFeatures(features)

    # Atualizar a camada
    layer.updateExtents()

    #Criar o layer de arestas sentido unico