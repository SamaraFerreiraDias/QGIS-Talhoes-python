#Obs: selecionar somente o layer "Linhas_De_Cana"
from qgis.core import *
from qgis.gui import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math

#Funcoes========================================================================
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def novoPonto(p1, p2, k):
    f = k / dist(p1, p2)
    v = [f*(p2[0] - p1[0]), f*(p2[1] - p1[1])]
    return QgsPointXY(p1[0] + v[0], p1[1] + v[1])
#===============================================================================

mapCanvas = iface.mapCanvas()
n = mapCanvas.layerCount()
layer = [mapCanvas.layer(i) for i in range(n)]
layer = layer[0]

#ordenar pelo campo FID
features = []
features = sorted(layer.getFeatures(), key=lambda x: x['fid'])

#ler lista de linhas e inverter ordem dos vertices nas linhas impares
fila = []
i = 0
for feat in features:
    geom = feat.geometry()
    #print feat['fid']
    if geom.type() == QgsWkbTypes.LineGeometry:
        linhas = geom.asMultiPolyline()
        for l in linhas:
            if (i % 2) != 0:
                l.reverse()
            fila += l
            fila.append(None)
            i += 1

fila.reverse() #para retirar do final

#gerar pontos de carga
cargaCheia = QInputDialog.getText(None, "Qgis" ,"Quantos metros para encher um transbordo? ")
cargaCheia = float(cargaCheia[0])
print('Produtividade: enche um transbordo a cada ', cargaCheia, ' metros.')

# criar o layer de arestas sentido unico
layerAresta = QgsVectorLayer("MultiLineString", "Arestas_" + str(cargaCheia), "memory" )
provider = layerAresta.dataProvider()
crs = layerAresta.crs()
crs.createFromId(31982)
layerAresta.setCrs(crs)
QgsProject.instance().addMapLayer(layerAresta)

#percorrer as linhas e calcular os pontos de carga
percorrido = 0
i = fila.pop()
j = []
pontosCarga = []
extremidades = [] #extremidades das cargas
entrada = i  #guarda a entrada da linha
aresta = [i]

while(len(fila) > 0):
    j = fila.pop()
    
    if j == None: #final da linha de cana
        #adicionar a aresta
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolylineXY(aresta))
        provider.addFeatures([feat])
        #adicionar extremidade de saida
        for e in range(len(extremidades)):
            if len(extremidades[e]) == 1:
                extremidades[e].append(aresta[len(aresta)-1])
        aresta = []
        if len(fila) > 0: #pular para prox linha
            i = fila.pop()
            entrada = i
            j = fila.pop()
            aresta.append(i)
            aresta.append(j)
        else:
            break   #finalizar o loop while
    else:
        aresta.append(j)

    aresta_ij = dist(i, j)
    
    if(percorrido + aresta_ij) <= cargaCheia:
        percorrido += aresta_ij
    else: #novo ponto
        k = cargaCheia - percorrido
        novoPto = novoPonto(i,j,k)
        pontosCarga.append(novoPto)
        percorrido = 0
        fila.append(j)
        j = novoPto
        #adicionar extremidade de entrada
        extremidades.append([entrada])
        #adicionar aresta meio de linha
        aresta.pop()
        aresta.append(novoPto)
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolylineXY(aresta))
        provider.addFeatures([feat])
        aresta = [novoPto]
    i = j

layerAresta.updateExtents()
print('Número de pontos de carga gerados: ', len(pontosCarga))

# criar o layer de cargas
newlayer = QgsVectorLayer( "Point", "Cargas_" + str(cargaCheia), "memory" )
provider = newlayer.dataProvider()
crs = newlayer.crs()
crs.createFromId(31982)
newlayer.setCrs(crs)
QgsProject.instance().addMapLayer(newlayer)

#criar cabeçalho dos tributos
provider.addAttributes([QgsField("ID", QVariant.Int)])
provider.addAttributes([QgsField("Nome", QVariant.String)])
provider.addAttributes([QgsField("Tipo", QVariant.String)])
provider.addAttributes([QgsField("Entrada_X", QVariant.Double)])
provider.addAttributes([QgsField("Entrada_Y", QVariant.Double)])
provider.addAttributes([QgsField("Saida_X", QVariant.Double)])
provider.addAttributes([QgsField("Saida_Y", QVariant.Double)])
newlayer.updateFields()

#adicionar pontos
id = 0
for i in range(len(pontosCarga)):
    nome = "C" + str(id + 1)
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPointXY(pontosCarga[i]))
    entrada = extremidades[i][0]
    saida = extremidades[i][1]
    feat.setAttributes([id, nome, "Carga", entrada.x(), entrada.y(), saida.x(), saida.y()])
    provider.addFeatures([feat])
    id += 1 
    
newlayer.updateExtents()
print('Executado com sucesso...')