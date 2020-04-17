from heapq import *


class MinHeap:

    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def push(self, item):
        heappush(self.heap, item)

    def pop(self):
        return heappop(self.heap)

