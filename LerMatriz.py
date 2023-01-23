#Matriz de distancias 'pontos de transbordo' x 'pontos de carga'
arq = open('matriz_distancias_250.txt', 'r')  
texto = [] 
matriz = []
Distancias = [] 

texto = arq.readlines() 

for i in texto:          
    matriz.append(i.split())

for i in range(len(matriz)):
    Distancias.append([])
    for j in range(len(matriz[i])):
        Distancias[i].append(float(matriz[i][j]))
print(Distancias)


arq.close()
