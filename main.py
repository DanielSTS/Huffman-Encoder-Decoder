import cv2
from MinHeap import *
from No import *
import numpy as np




#Percorre a imagem e acumula as ocorrências de cada valor de pixel

def criar_dicionario_freq(imagem):

    linha, coluna = imagem.shape

    frequencias = {}

    for i in range(linha):
        for j in range(coluna):
            pixel = imagem[i][j]
            if pixel not in frequencias:
                frequencias[pixel] = 0
            frequencias[pixel] += 1
    return frequencias




def criar_heap(frequencias):

    h = MinHeap()

    for i in frequencias:
        no = No(i, frequencias[i])
        h.push(no)
    return h



# Criar a arvore, removendo os dois menores valores do heap para criar o no pai

def criar_arvore(heap):

    while len(heap) > 1:
        esquerda = heap.pop()
        direita = heap.pop()
        pai = No(None, esquerda.freq + direita.freq)
        pai.esquerda = esquerda
        pai.direita = direita
        heap.push(pai)




# A partir da árvore, cria o código de huffman correspondente a cada valor de pixel

def criar_codigo(raiz, codigo_atual,codigos):

    if raiz is None:
        return codigos

    if raiz.pixel is not None:
        codigos[raiz.pixel] = codigo_atual
        return

    #Chama recursivamente para a esquerda

    criar_codigo(raiz.esquerda, codigo_atual + "0",codigos)

    #Chama recursivamente para a direita

    criar_codigo(raiz.direita, codigo_atual + "1",codigos)



#cria uma string contendo as dimensões da imagem, dicionário de códigos e os códigos de cada pixel da imagem

def codificar_string(imagem,frequencias,codigos):

    codigo_imagem = ""
    linha, coluna = imagem.shape
    codigo_imagem+="{0:016b}".format(linha)
    codigo_imagem+= "{0:016b}".format(coluna)  #Primeiros 4 bytes do arquivo será sobre o shape da imagem
    codigo_imagem += "{0:8b}".format(len(frequencias) - 1)  #Proximos 2 bytes pra o tamanho do dicionário



    for i in frequencias: #Próximos bytes do arquivo armazenarão o dicionário de frequências
        codigo_imagem += "{0:08b}".format(int(i))  #Valor de pixel cabe em 8bits
        codigo_imagem += "{0:024b}".format(int(frequencias[i]))  #Valor de código cabe em 24 bits


    for i in range(linha):
        for j in range(coluna):
            codigo_imagem += codigos[imagem[i][j]]



    return codigo_imagem


#Converte a string em um array de bytes para poder armazenar em um arquivo.bin

def codificar_bytes(string_dados):

    while (len(string_dados) % 8 != 0):
        string_dados += "0"


    dados = bytearray()

    #Converte de 8  em 8 caracteres a um byte e adiciona ao array de bytes
    for i in range(0, len(string_dados), 8):
        dados.append(int(string_dados[i:i + 8], 2))


    return dados



#Reconstrói a imagem a partir dos códigos de cada pixel, e a arvore de hufmman passada


def decodificar(string_dados,raiz,linha,coluna):
    raiz1  = raiz
    vetor= []
    for i in (string_dados):
        if(i =="0"):
            raiz= raiz.esquerda
        if(i =="1"):
            raiz = raiz.direita
        if(raiz.esquerda == None and raiz.direita == None):
            vetor.append(raiz.pixel)
            raiz = raiz1

    matriz = np.array(vetor).reshape(linha,coluna)

    return matriz




#Comprime uma imagem.tiff em imagem.bin, passado como parametro o caminho da imagem e o nome do arquivo quando compactado

def comprimir(caminho,nome):

    imagem = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)
    frequencias = criar_dicionario_freq(imagem)
    heap = criar_heap(frequencias)
    criar_arvore(heap)
    raiz = heap.pop()
    codigos = {}
    criar_codigo(raiz, "",codigos)
    string = codificar_string(imagem,frequencias,codigos)
    array_bytes = codificar_bytes(string)

    with open(nome +".bin", "wb") as arquivo:
        arquivo.write(bytes(array_bytes))
    return True


#Comprime uma imagem.bin em imagem.tiff, passado como parametro o caminho da imagem compactada e o nome para o arquivo quando for descompactada

def descomprimir(caminho,nome):

    with open(caminho, "rb") as arquivo:
        string_codificada = ""
        linha=""
        coluna=""
        len_dicionario=""
        freq = {}
        aux = True
        byte = arquivo.read(1)
        while len(byte) > 0:
            if(aux == True):  #Pega os 2 primeiros bytes para a linha, os próximos 2 bytes para coluna e o próximos 2 para o tamanho do dicionário

                linha += f"{bin(ord(byte))[2:]:0>8}"
                byte = arquivo.read(1)
                linha += f"{bin(ord(byte))[2:]:0>8}"
                byte = arquivo.read(1)

                coluna += f"{bin(ord(byte))[2:]:0>8}"
                byte = arquivo.read(1)
                coluna += f"{bin(ord(byte))[2:]:0>8}"
                byte = arquivo.read(1)

                len_dicionario += f"{bin(ord(byte))[2:]:0>8}"
                byte = arquivo.read(1)
                #len_dicionario += f"{bin(ord(byte))[2:]:0>8}"
                #byte = arquivo.read(1)


                for i in range(int(len_dicionario,2) + 1):

                    chave = f"{bin(ord(byte))[2:]:0>8}"
                    byte = arquivo.read(1)

                    valor = ""
                    valor += f"{bin(ord(byte))[2:]:0>8}"
                    byte = arquivo.read(1)
                    valor += f"{bin(ord(byte))[2:]:0>8}"
                    byte = arquivo.read(1)
                    valor += f"{bin(ord(byte))[2:]:0>8}"
                    byte = arquivo.read(1)

                    freq[int(chave,2)] = int(valor,2)

                aux = False

            else:
                string_codificada += f"{bin(ord(byte))[2:]:0>8}"
                byte = arquivo.read(1)

        #Construir a árvore de hufman
        heap = criar_heap(freq)
        criar_arvore(heap)
        raiz = heap.pop()
        matriz = decodificar(string_codificada,raiz,int(linha,2),int(coluna,2))
        cv2.imwrite(str(nome) + ".tiff", matriz)
        return True




while(True):

    print("Digite 1 para comprimir ou 2 para descomprimir ou 0 para encerrar o programa")
    a = int(input())

    if( a ==1 ):
        print("Digite o caminho da imagem: ex(arquivo.tiff)")
        caminho = input()
        print("Digite o nome para o arquivo de saída:")
        nome_saida = input()
        controle = comprimir(caminho, nome_saida)
        if (controle):
            continue
    elif(a==2):
        print("Digite o caminho do arquivo compactado: ex(arquivo.bin)")
        caminho = input()
        print("Digite o nome para o arquivo de saída")
        nome_saida = input()
        controle = descomprimir(caminho,nome_saida)
        if(controle):
            continue
    else:
        break

'''comprimir("LEFT_4k3d_2160p24_003900.tiff","compactado1")


descomprimir("compactado1.bin","descompactado1")

comprimir("LEFT_4k3d_2160p24_010512.tiff","compactado2")

descomprimir("compactado2.bin","descompactado2")'''





