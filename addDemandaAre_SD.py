#Obs selecionar layer Arestas_SD e selecionar a edição do layer
#Gerar separadamente cada coluna comentando o código e apertando no lapis

from qgis.core import QgsField, QgsFeature, QgsGeometry, QgsVectorLayer
from PyQt5.QtCore import QVariant

# Obtenha o layer ativo
#layer = iface.activeLayer()

# Adicione a nova coluna 'distancia' à tabela de atributos
#layer.dataProvider().addAttributes([QgsField("distancia", QVariant.Double)])
#layer.updateFields()

# Crie uma função para calcular a distância de uma linha
#def calcDistance(geometry):
#    distance_area = QgsDistanceArea()
#    return distance_area.measureLength(geometry)

# Use uma estrutura de loop para percorrer cada linha no layer
#for feature in layer.getFeatures():
#    geometry = feature.geometry()
#    distance = calcDistance(geometry)

    # Atualize o valor da nova coluna 'distancia' para cada linha
#    layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("distancia"), distance)

# Atualize o layer
#layer.updateFeature(feature)

#================================================================================
# Obtenha o layer ativo
#layer = iface.activeLayer()

# Adicione a nova coluna 'demanda' à tabela de atributos
#layer.dataProvider().addAttributes([QgsField("demanda", QVariant.Double)])
#layer.updateFields()

# Use uma estrutura de loop para percorrer cada linha no layer
#for feature in layer.getFeatures():
    # Pega o valor da coluna 'distancia'
#    distance = feature['distancia']
    # calcula o valor da coluna 'demanda'
#    demand = distance * 0

    # Atualize o valor da nova coluna 'demanda' para cada linha
#    layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("demanda"), demand)

# Atualize o layer
#layer.updateFeature(feature)
#================================================================================
layer = iface.activeLayer()

# Adicione a nova coluna 'tipo' à tabela de atributos
layer.dataProvider().addAttributes([QgsField("tipo", QVariant.String)])
layer.updateFields()

# Use uma estrutura de loop para percorrer cada linha no layer
for feature in layer.getFeatures():
    # Atribuir a string "SD" para a coluna 'tipo'
    layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("tipo"), "SD")

# Atualize o layer
layer.updateFeature(feature)
