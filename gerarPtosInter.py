#Obs: selecionar somente o layer "Linhas_De_Cana"
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import QVariant

mapCanvas = iface.mapCanvas()
n = mapCanvas.layerCount()
layer = [mapCanvas.layer(i) for i in range(n)]
layer = layer[0]
linhas = []

for feat in layer.getFeatures():
    geom = feat.geometry()
    if geom.type() == QgsWkbTypes.LineGeometry:
        mPLinha = geom.asMultiPolyline()
        for i in mPLinha:
            linhas.append(i)

#criar novo layer
novoLayer = QgsVectorLayer("Point", "Intermediarios", "memory")
crs = novoLayer.crs()
crs.createFromId(29192)
novoLayer.setCrs(crs)
QgsProject.instance().addMapLayer(novoLayer)

#criar cabeçalho dos tributos
provider = novoLayer.dataProvider()
provider.addAttributes([QgsField("ID", QVariant.Int)])
provider.addAttributes([QgsField("Nome", QVariant.String)])
provider.addAttributes([QgsField("Tipo", QVariant.String)])
novoLayer.updateFields()

#selecionando o primeiro e o ultimo ponto de cada linha
ptosInter = list()
for linha in linhas:
    ptosInter.append(linha[0])
    ptosInter.append(linha[len(linha) - 1])

#adicionando os pontos em um novo layer
id = 0
for p in ptosInter:
    nome = "I" + str(id + 1)
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPointXY(p))
    feat.setAttributes([id, nome, "Intermediario"])
    provider.addFeatures([feat])
    id += 1
    
novoLayer.updateExtents()
print('Executado com sucesso...')





