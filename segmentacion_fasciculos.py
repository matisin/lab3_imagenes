import numpy
import os
import threading

from read_write_bundles import *

def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

atlas_path = 'atlas_faisceaux_MNI'
brain_path = 'whole_brain_MNI_100k_21p.bundles'

fasciculos_atlas = []

for root, dirs, files in os.walk(atlas_path):
    for filename in files:
        if 'data' not in filename:
            path = os.path.join(atlas_path, filename)
            fasciculo = read_bundle(path)
            fasciculos_atlas.append(fasciculo)

whole_brain = read_bundle(brain_path)
whole_brain_chunks = list(chunks(whole_brain, 10000))
umbral = 9

def distance(id):
    brain_chunk = whole_brain_chunks[id]
    for fasciculo_atlas in fasciculos_atlas:
        for fibra_atlas in fasciculo_atlas:
            for index,fibra_datos in enumerate(brain_chunk):
                umbral_exit = False
                max_1 = 0
                max_2 = 0
                n = len(fibra_datos)
                for i in range(0, n):
                    a = fibra_atlas[i]
                    b_1 = fibra_datos[i]
                    b_2 = fibra_datos[n - 1 - i]
                    dist_1 = numpy.linalg.norm(a - b_1)
                    dist_2 = numpy.linalg.norm(a - b_2)
                    if dist_1 > max_1:
                        max_1 = dist_1
                    if dist_2 > max_2:
                        max_2 = dist_2
                    if min(max_1,max_2) > umbral:
                        umbral_exit = True
                        break
                if umbral_exit:
                    continue
                dist = min(max_1, max_2)
                if dist < umbral:
                    brain_chunk.pop(index)
                    print("ok")
                    break

class myThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        distance(self.threadID - 1)

# Create new threads
thread1 = myThread(1)
thread2 = myThread(2)
thread3 = myThread(3)
thread4 = myThread(4)
thread5 = myThread(5)
thread6 = myThread(6)
thread7 = myThread(7)
thread8 = myThread(8)
thread9 = myThread(9)
thread10 = myThread(10)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()
thread9.start()
thread10.start()
