#Obs: selecionar os layers: Transbordos, Intermediarios, Cargas, Arestas_SD
from qgis.core import *
from qgis.gui import *
import math
import os

#===============================================================================
#Estruturas de dados globais
vertices = []
vert_nomes = []
cargas = []  #Pontos de carga
transbordos = []  #Pontos de transbordos
intermediarios = []  #Pontos intermediarios
arestas = []
arestasComp = []
eArestaSD = []
matrizAdj = []   #matriz de distancias adjacentes do floyd
tolerancia = 10**(-6)
NAOENCONTRADO = -1
INF = float("inf")
LAYER_SD = "Arestas_SD"
pasta = os.path.join(os.path.expanduser('~'), 'Documents')

#===============================================================================
#Calcula a distancia entre dois pontos
def dist (p1, p2):
    return math.sqrt( (p1.x() - p2.x())** 2 + (p1.y() - p2.y())** 2)

#função para procurar os vertices na lista
def procVert (pto):
    for i in range(len(vertices)):
        d = dist(pto, vertices[i])
        if d < tolerancia:
            return i
    else:
        return NAOENCONTRADO

#Imprimir matriz
def printMatriz (A):
    M = len(A)
    for i in range(M):
        N = len(A[i])
        for j in range(N):
            print(round (A[i][j], 1), "\t", end= " ")
        print ('')

#Algorítimo de Floyd Wharshall (Caminho Mínimo)
def floyd (grafo):
    distMin = grafo
    len_matrix = len(grafo)
         
    #Aplicação do algorítmo
    for k in range(len_matrix):
        for i in range(len_matrix):
            for j in range(len_matrix):
                distMin[i][j] = min(distMin[i][j], distMin[i][k] + distMin[k][j])
    return distMin

def criarMatriz(nLin, nCol, valor):
    Matriz = []
    for i in range(nLin):
        linha = []
        for j in range(nCol):
            linha.append(valor)
        Matriz.append(linha)
    return Matriz

#salvar matriz num arquivo
def salvarMatriz (A, fileName):
    f = open(fileName, "w")
    M = len(A)
    f.write(str(M) + '\n')
    f.write(str(len(A[0])) + '\n')
    for i in range(M):
        N = len(A[i])
        sep = ", "
        for j in range(N):
            if(j == N-1):
                sep = ""
            f.write(str(round (A[i][j], 1)) + sep)
        f.write('\n')
    f.close()

#salvar matriz do modelo num arquivo
def salvarMatrizModelo (A, fileName):
    f = open(fileName, "w")
    NC = len(A)
    NT = len(A[0])
    f.write('Cargas: ' + str(NC) + "\n")
    f.write('Transbordos: ' + str(NT) + "\n")
    
    f.write(',')
    for t in range(NT):
        f.write(transbordos[t][1])
        if(t < NT-1):
            f.write(',')
    
    f.write("\n")
    for c in range(NC):
        f.write(cargas[c][1] + ',')
        for t in range(NT):
            f.write(str(round(A[c][t], 1)))
            if(t < NT-1):
                f.write(',')
        f.write("\n")
    f.close()

def salvarMatrizDistMinIT (A, fileName):
#salva a matriz de distancias minimas de todos os pontos
#intermediarios para todos os pontos de transbordo
    f = open(fileName, "w")
    NI = len(intermediarios)
    NT = len(transbordos)
    f.write('Inter: ' + str(NI) + '\n')
    f.write('Transbordos: ' + str(NT) + '\n')
    
    f.write(',')
    for t in range(NT):
        f.write(transbordos[t][1])
        if(t < NT-1):
            f.write(", ")
    
    f.write('\n')
    for i in range(NI):
        f.write(intermediarios[i][1] + ', ')
        idx_i = intermediarios[i][3]
        
        for t in range(NT):
            idx_t = transbordos[t][3]
            
            f.write(str(round(A[idx_i][idx_t], 1)))
            if(t < NT-1):
                f.write(", ")
        f.write('\n')
    f.close()

def salvarMatrizDistMin (A, fileName):
#salva a matriz de distancias minimas
    f = open(fileName, "w")
    N = len(A)
    
    f.write(',')
    for i in range(N):
        f.write(vert_nomes[i])
        if(i < N-1):
            f.write(", ")
    
    f.write('\n')
    for i in range(N):
        f.write(vert_nomes[i] + ', ')
        
        for j in range(N):
            f.write(str(round(A[i][j], 1)))
            
            if(j < N-1):
                f.write(", ")
        f.write('\n')
    f.close()

def salvarArestas (A, fileName):
#salva as arestas da matriz de adjacencia
    f = open(fileName, "w")
    N = len(A)
    cnt = 0
    for i in range(N):
        for j in range(i+1, N):
            if(A[i][j] != 0 and A[i][j] != INF):
                cnt = cnt + 1
                if(A[i][j] == A[j][i]):
                    linha = str(vert_nomes[i]) + "," + str(vert_nomes[j]) + "\n"
                    f.write(linha)
    f.close()
    print("Arestas salvas: ", cnt)
    
#===============================================================================
#Selecionando os layers ativos
mapCanvas = iface.mapCanvas()
n = mapCanvas.layerCount()
layers = [mapCanvas.layer(i) for i in range(n)]

#Separando os layers
layerLinhas = []
layerPontos = []
for l in layers:
    #print(l.name(), " ", l.geometryType())
    if l.geometryType() == QgsWkbTypes.LineGeometry:
        layerLinhas.append(l)
    if l.geometryType() == QgsWkbTypes.PointGeometry:
        layerPontos.append(l)

#Criar uma lista de cargas, transbordos, intermediarios, e uma lista de vertices do grafo
#Somente os pontos de transbordo e intermediarios entram no grafo
for l in layerPontos:
    #print(l.name())
    for f in l.getFeatures():
        vert = f.geometry().asPoint()
        #print(f.attributes()[0])
        
        attr = f.attributes()
        idx = f.fieldNameIndex('Tipo')
        
        if attr[idx] == "Transbordo":
            vertices.append(vert)
            vert_nomes.append(attr[1])
            attr.append(len(vertices) -1)   #posicao na lista de vertices
            transbordos.append(attr)
        if attr[idx] == "Intermediario":
            vertices.append(vert)
            vert_nomes.append(attr[1])
            attr.append(len(vertices) -1)
            intermediarios.append(attr)   #posicao na lista de vertices
        if attr[idx] == "Carga":
            cargas.append(attr)

#Criar uma lista de arestas
for l in layerLinhas:
    #print("features: ", l.featureCount())
    for f in l.getFeatures():
        mPLinha = f.geometry().asMultiPolyline()
        arestasComp.append(f.geometry().length())
        for i in mPLinha:
            arestas.append(i)
            if l.name() == LAYER_SD:
               eArestaSD.append(True)
            else:
               eArestaSD.append(False)

#Criar matriz distâncias
numVert = len(vertices)
print("Numero de vertices: ", numVert)
print("Numero de arestas: ", len(arestas))
print("Criando matriz ...")

#Inicializar a matriz de adjacencia do floyd
for i in range(numVert):
    linha = []
    for j in range(numVert):
        if i == j:
            linha.append(0)
        else:
            linha.append(INF)
    matrizAdj.append(linha)

#Preencher a matriz de adjacencia do floyd
for k in range(len(arestas)):
    a = arestas[k]
    i = procVert(a[0])
    j = procVert(a[len(a)-1])
    if i != NAOENCONTRADO and j != NAOENCONTRADO:
        matrizAdj[i][j] = arestasComp[k]
        if eArestaSD[k] == True:
            matrizAdj[j][i] = arestasComp[k]
    else:
        print("Aresta não identificada!")


#salvarArestas(matrizAdj, pasta + "Arestas.csv")
#salvarMatrizDistMin(matrizAdj, pasta + "matrizAdj.csv")
#print("\nMatriz de adjacência: ")
#printMatriz(matrizAdj)

#calcular caminhos minimo
matrizDistMin = floyd(matrizAdj)

#print("\nMatriz de distancias minimas: ")
#printMatriz(matrizDistMin)

#Iniciando matriz MOD1
NC = len(cargas)
NT = len(transbordos)
matrizModel = criarMatriz(NC, NT, 0)

for c in range(NC):
    #pontos de entrada e saida na linha de cana da carga
    ptoEntrada = QgsPointXY(cargas[c][3], cargas[c][4])
    ptoSaida = QgsPointXY(cargas[c][5], cargas[c][6])
    
    #procurar os pontos intermediarios de entrada e saida
    e = procVert(ptoEntrada)
    s = procVert(ptoSaida)

    for t in range(NT):
        j = transbordos[t][3]
        matrizModel[c][t] = matrizDistMin[s][j] + matrizDistMin[j][e]

#salvarMatrizDistMin(matrizDistMin, pasta + "matrizDistanciaMinimas_1000.csv")
salvarMatrizModelo(matrizModel, pasta + "/matrizModelo_250.csv")
#salvarMatrizDistMinIT(matrizDistMin, pasta + "matrizDistanciaIT.csv")

print('Executado com sucesso...')
