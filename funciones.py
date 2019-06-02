import sys
import os
from PIL import Image
from multiprocessing import Process, Queue, cpu_count
#se pueden modificar
TILE_SIZE      = 50		# alto y ancho
TILE_MATCH_RES = 5		# encaja con la resolucion original
ENLARGEMENT    = 8

TILE_BLOCK_SIZE = TILE_SIZE / max(min(TILE_MATCH_RES, TILE_SIZE), 1)
WORKER_COUNT = max(cpu_count() - 1, 1)
OUT_FILE = 'mosaico_creado.jpg'
EOQ_VALUE = None



class Procesador_img:
	def __init__(self, directorio_img):
		self.directorio_img = directorio_img

	def __img_proceso(self, ruta_img):
		try:
			img = Image.open(ruta_img)
			w = img.size[0]
			h = img.size[1]
			dimension_minima = min(w, h)
			ancho_recortado = (w - dimension_minima) / 2
			alto_recortado = (h - dimension_minima) / 2
			img = img.crop((ancho_recortado, alto_recortado, w - ancho_recortado, h - alto_recortado))

			img_larga = img.resize((TILE_SIZE, TILE_SIZE), Image.ANTIALIAS)
			img_corta = img.resize((TILE_SIZE/TILE_BLOCK_SIZE, TILE_SIZE/TILE_BLOCK_SIZE), Image.ANTIALIAS)

			return (img_larga.convert('RGB'), img_corta.convert('RGB'))
		except:
			return (None, None)

	def obt_imganes(self):
		imagenes_largo_array = []
		imagenes_corto_array = []


		# buscnado en el directorio
		for root, subFolders, archivos in os.walk(self.directorio_img):
			for img_nombre in archivos:
				ruta_img = os.path.join(root, img_nombre)
				large_tile, small_tile = self.__img_proceso(ruta_img)
				if large_tile:
					imagenes_largo_array.append(large_tile)
					imagenes_corto_array.append(small_tile)


		return (imagenes_largo_array, imagenes_corto_array)

class Objeto_Image:
	def __init__(self, ruta_imagen):
		self.ruta_imagen = ruta_imagen

	def get_data(self):
		img = Image.open(self.ruta_imagen)
		w = img.size[0] * ENLARGEMENT
		h = img.size[1]	* ENLARGEMENT
		imagen_largo_objeto = img.resize((w, h), Image.ANTIALIAS)
		diferencia_ancho_objeto = (w % TILE_SIZE)/2
		diferencia_alto_objeto = (h % TILE_SIZE)/2

		if diferencia_ancho_objeto or diferencia_alto_objeto:
			imagen_largo_objeto = imagen_largo_objeto.crop((diferencia_ancho_objeto, diferencia_alto_objeto, w - diferencia_ancho_objeto, h - diferencia_alto_objeto))

		img_peque = imagen_largo_objeto.resize((w/TILE_BLOCK_SIZE, h/TILE_BLOCK_SIZE), Image.ANTIALIAS)

		img_datos_obj = (imagen_largo_objeto.convert('RGB'), img_peque.convert('RGB'))


		return img_datos_obj

class Encaje_img:
	def __init__(self, pic_datos):
		self.pic_datos = pic_datos

	def __diferencia_obteniendo_imagen(self, tras1, tras2, se_sale_del_valor):
		diferencia = 0
		for i in range(len(tras1)):
			diferencia += ((tras1[i][0] - tras2[i][0])**2 + (tras1[i][1] - tras2[i][1])**2 + (tras1[i][2] - tras2[i][2])**2)
			if diferencia > se_sale_del_valor:
				return diferencia
		return diferencia

	def obte_mejor_encaje_img(self, img_datos):
		obte_mejor_encaje_img_indexadaando = None
		diferencia_minima = sys.maxint
		img_indexada = 0

#Buscando el mejor encaje
		for dato_imagen_encaje in self.pic_datos:
			diferencia = self.__diferencia_obteniendo_imagen(img_datos, dato_imagen_encaje, diferencia_minima)
			if diferencia < diferencia_minima:
				diferencia_minima = diferencia
				obte_mejor_encaje_img_indexadaando = img_indexada
			img_indexada += 1

		return obte_mejor_encaje_img_indexadaando

def img_encaja(trabajo_img, resultado_trazo, pic_datos):
	tile_fitter = Encaje_img(pic_datos)

	while True:
		try:
			img_datos, direcciones_img = trabajo_img.get(True)
			if img_datos == EOQ_VALUE:
				break
			img_indexada = tile_fitter.obte_mejor_encaje_img(img_datos)
			resultado_trazo.put((direcciones_img, img_indexada))
		except KeyboardInterrupt:
			pass

	resultado_trazo.put((EOQ_VALUE, EOQ_VALUE))

class Proceso_trazo:
	def __init__(self, total):
		self.total = total
		self.counter = 0

	def update(self):
		self.counter += 1
    	sys.stdout.flush();

class mosaico_creadoImage:
	def __init__(self, original_img):
		self.image = Image.new(original_img.mode, original_img.size)
		self.x_tile_count = original_img.size[0] / TILE_SIZE
		self.y_tile_count = original_img.size[1] / TILE_SIZE
		self.total_tiles  = self.x_tile_count * self.y_tile_count

	def img_agreg(self, dato_imagen_encaje, direcciones):
		img = Image.new('RGB', (TILE_SIZE, TILE_SIZE))
		img.putdata(dato_imagen_encaje)
		self.image.paste(img, direcciones)

	def save(self, path):
		self.image.save(path)

def build_mosaico_creado(resultado_trazo, todos_img_dat, original_img_large):
	mosaico_creado = mosaico_creadoImage(original_img_large)

	active_workers = WORKER_COUNT
	while True:
		try:
			direcciones_img, obte_mejor_encaje_img_indexadaando = resultado_trazo.get()

			if direcciones_img == EOQ_VALUE:
				active_workers -= 1
				if not active_workers:
					break
			else:
				dato_imagen_encaje = todos_img_dat[obte_mejor_encaje_img_indexadaando]
				mosaico_creado.img_agreg(dato_imagen_encaje, direcciones_img)

		except KeyboardInterrupt:
			pass

	mosaico_creado.save(OUT_FILE)

def creando(original_img, tiles):
	original_img_large, original_img_small = original_img
	tiles_large, tiles_small = tiles

	mosaico_creado = mosaico_creadoImage(original_img_large)

	todos_img_dat = map(lambda tile : list(tile.getdata()), tiles_large)
	all_tile_data_small = map(lambda tile : list(tile.getdata()), tiles_small)

	trabajo_img   = Queue(WORKER_COUNT)
	resultado_trazo = Queue()

	try:
		Process(target=build_mosaico_creado, args=(resultado_trazo, todos_img_dat, original_img_large)).start()

		for n in range(WORKER_COUNT):
			Process(target=img_encaja, args=(trabajo_img, resultado_trazo, all_tile_data_small)).start()

		progress = Proceso_trazo(mosaico_creado.x_tile_count * mosaico_creado.y_tile_count)
		for x in range(mosaico_creado.x_tile_count):
			for y in range(mosaico_creado.y_tile_count):
				large_box = (x * TILE_SIZE, y * TILE_SIZE, (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE)
				small_box = (x * TILE_SIZE/TILE_BLOCK_SIZE, y * TILE_SIZE/TILE_BLOCK_SIZE, (x + 1) * TILE_SIZE/TILE_BLOCK_SIZE, (y + 1) * TILE_SIZE/TILE_BLOCK_SIZE)
				trabajo_img.put((list(original_img_small.crop(small_box).getdata()), large_box))
				progress.update()


	finally:
		for n in range(WORKER_COUNT):
			trabajo_img.put((EOQ_VALUE, EOQ_VALUE))

def mosaico_creado(img_path, tiles_path):
	pic_datos = Procesador_img(tiles_path).obt_imganes()
	img_datos_obj = Objeto_Image(img_path).get_data()
	creando(img_datos_obj, pic_datos)
