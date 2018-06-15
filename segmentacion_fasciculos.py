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
n_threads = 10
chunk = 100000 / n_threads
whole_brain_chunks = list(chunks(whole_brain, int(chunk)))
umbral = 10

def distance(id):
    count = 0
    brain_chunk = whole_brain_chunks[id]
    for fibra_datos in brain_chunk:
        brain_data_exit = False
        for fasciculo_atlas in fasciculos_atlas:
            for fibra_atlas in fasciculo_atlas:
                umbral_exit = False
                max_1 = 0
                max_2 = 0
                for i in range(0, 21):
                    a = fibra_atlas[i]
                    b_1 = fibra_datos[i]
                    b_2 = fibra_datos[20 - i]
                    dist_1 = numpy.linalg.norm(a - b_1)
                    dist_2 = numpy.linalg.norm(a - b_2)
                    if dist_1 > max_1:
                        max_1 = dist_1
                    if dist_2 > max_2:
                        max_2 = dist_2
                    if dist_1 and dist_2 > umbral:
                        umbral_exit = True
                        break
                if umbral_exit:
                    continue
                dist = min(max_1, max_2)
                if dist < umbral:
                    brain_data_exit = True
                    count+=1
                    break
            if brain_data_exit:
                break
        if brain_data_exit:
            continue
    print('id: {}, count {}'.format(id,count))

class myThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.count = 0

    def run(self):
        distance(self.threadID)

myThread(0).start()
'''for i in range(0,n_threads):
    myThread(i).start()'''