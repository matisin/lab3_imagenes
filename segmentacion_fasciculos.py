import threading
import time
import numpy

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from mpl_toolkits import mplot3d

from read_write_bundles import *
from apscheduler.schedulers.background import BackgroundScheduler

#funcion para dividir arreglos en pedazos de mismo largo.
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

atlas_path = 'atlas_faisceaux_MNI'
brain = 'whole_brain_MNI_100k_21p'
brain_file = brain + '.bundles'
save_path = brain + '_faisceaux_MNI'

if not os.path.exists(save_path):
    os.makedirs(save_path)

fasciculos_atlas = []
filenames = []

#esto es para obtener los nombres de los archivos en atlas_faisceaux_MNI para leer los fasciculos y guardarlos en el
#arreglo fasciculos_atlas. Tambien se guarda el nombre de los archivos en filenames pero se cambia atlas por
#whole_brain_MNI_100k_21p
for root, dirs, files in os.walk(atlas_path):
    for filename in files:
        if 'data' not in filename:
            path = os.path.join(atlas_path, filename)
            fasciculo = read_bundle(path)
            fasciculos_atlas.append(fasciculo)
            region = filename.replace('.bundles','')
            region = region.replace('atlas','')
            new_filename = brain + region
            filenames.append(new_filename)

#El cerebro se reduce a un tamano de 100000 fibras
whole_brain = read_bundle(brain_file)

#Se define una cantidad de hilos para hacer un procesamiento en paralelo, el cerebro se divide por la cantidad de hilos
# y se guardan estas divisiones en part_brain_chunks
n_threads = 10
chunk = len(whole_brain) / n_threads
whole_brain_chunks = list(chunks(whole_brain, int(chunk)))

#segmentation es modificado en la funcion sementacion_fibras, aqui cada hilo asocia el indice de una fibra en part_brain_chunks
# con el nombre del archivo de fasciculo si la fibra se encuentra dentro del ubral en alguna fibra de algun fasciculo
segmentation = dict()
def segmentacion_fibras(id):
    umbral = 10
    brain_chunk = whole_brain_chunks[id]
    for index_brain, fibra_datos in enumerate(brain_chunk):
        brain_data_exit = False
        for index_fasciculo,fasciculo_atlas in enumerate(fasciculos_atlas):
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
                    if dist_1 > umbral and dist_2 > umbral:
                        umbral_exit = True
                        break
                if umbral_exit:
                    continue
                dist = min(max_1, max_2)
                if dist < umbral:
                    brain_data_exit = True
                    index = id * 1000 + index_brain
                    segmentation[index] = (fibra_datos,filenames[index_fasciculo])
                    break
            if brain_data_exit:
                break
        if brain_data_exit:
            continue

#metodo que muestra el tiempo que ha pasado desde que empezo a ejectuarse el algoritmo y cuantas fibras han sido etique-
#tadas
def segmentation_print(start):
    found = len(segmentation)
    end = time.time()
    elapsed = end - start
    print '\rtime: {} etiquetados: {}'.format(int(elapsed), found),

#Hilos que ejecutan el metodo segmentacion_fibras sobre un indice que representa la posicion de la parte del cerebro a
#procesar
class myThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        segmentacion_fibras(self.threadID)

#se crean los hijlos y se guardan en un arreglo
threads = []
for i in range(0,n_threads):
    thread = myThread(i)
    threads.append(thread)
    break

#Se toma el tiempo antes de ejecutar el algoritmo, luego los hilos son ejecutados y se espera a que todos terminen para
#medir el tiempo final y continuar con la ejecucion del programa

print 'starting',
sched = BackgroundScheduler()
start = time.time()
sched.add_job(segmentation_print, 'interval', seconds=1, args=[start])
sched.start()
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
sched.shutdown()

filenames_count = dict(zip(filenames, [0] * len(filenames)))
#se guardan los datos con write_bundle y se cuentan las fibras
for data_and_file in segmentation.values():
    filename = data_and_file[1]
    count = filenames_count[filename] + 1
    filenames_count[filename] = count
    outfile = save_path + '/' + filename
    fibra_datos = data_and_file[0]
    write_bundle(outfile, fibra_datos)

#colores para el dibujo de fibras, mapean algunos colores con los fasciculos en un diccionario
colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
sorted_names = [name for hsv, name in by_hsv]
colors_fasciculo = dict(zip(filenames, sorted_names))

#grafico para plotear el cerebro
fig = plt.figure(figsize=(30, 20))
ax = plt.axes(projection='3d')

#se plotean las fibras del pedazo del cerebro como color gris
xline,yline,zline = [], [], []
for fibra in whole_brain:
    x, y, z = [], [], []
    for point in fibra:
        x.append(point[0])
        y.append(point[1])
        z.append(point[2])
    ax.plot3D(x, y, z, 'gray')

#se plotean las fibras segmentadas por fasciculo del atlas
for data_and_file in segmentation.values():
    fibra_datos = data_and_file[0]
    filename = data_and_file[1]
    x, y, z = [], [], []
    for point in fibra_datos:
        x.append(point[0])
        y.append(point[1])
        z.append(point[2])
    ax.plot3D(x, y, z, colors_fasciculo[filename])

#grafico mostrando la cantidad de fibras por fasciculo
graph = plt.figure()
ax = plt.subplot(111)

#se plotean la cantidad de fibras por fasciculo como grafico de barras con su respectivo color
colorlist = []
for label in list(filenames_count.keys()):
   colorlist.append(colors_fasciculo[label])
labels = list(filenames_count.keys())
for i in range(0, len(labels)):
    labels[i] = labels[i].replace(brain+'_','')
    labels[i] = labels[i].replace('_MNI','')
ax.bar(list(filenames_count.keys()), list(filenames_count.values()), linewidth=100, color=colorlist)
ax.set_xticklabels(labels, rotation=90)
plt.tight_layout()

plt.show()