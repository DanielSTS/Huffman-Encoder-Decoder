class No:

    def __init__(self, pixel, freq, esquerda=None,direita=None):

        self.pixel = pixel
        self.freq = freq
        self.esquerda = esquerda
        self.direita = direita

    def __lt__(self, other):
        return self.freq < other.freq

