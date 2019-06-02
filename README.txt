Mosaico de imágenes en Python
Junio 2019


Deberá usar Python, por lo que se recomienda actualizarlo o ya sea descargarlo.

Este programa crea un mosaico de una imagen de entrada con imagenes de un directorio, si desea descargar imágenes de perritos
dirijase al siguiente link:
https://www.kaggle.com/jessicali9530/stanford-dogs-dataset

Para ejecutar el programa debera tener las siguientes librerías de Python
-opencv
-matplotlib
-numpy

Se realiza de la siguiente manera:

-Si su computadora trabaja con sistema operativo de Windows,
ejecute lo sigueinte en la línea de comandos o consola:
python get-pip.py to install pip
pip3 install opencv-python
pip3 install matplotlib
pip3 install numpy-python

-Si su computadora trabaja con sistema operativo de Mac o Linux,
ejecute lo sigueinte en la línea de comandos o consola:
curl -O https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip3 install opencv-python
sudo pip3 install matplotlib
sudo pip3 install numpy

Para correr el programa debera ejecutar el siguiente comando:

python main.py imagen.jpg directorio

Donde imagen.jpg es la imagen a convertir (si la imagen tiene otra extension, ponerselo, por ejemplo
si es png poner imagen.png) y directorio es el directorio de imagenes con los que se creará el mosaico.
