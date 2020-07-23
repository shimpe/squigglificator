import numpy as np
import io
from PIL import Image
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QBuffer

def qimage_to_numpy_array(incomingQImage):
    incomingQImage = incomingQImage.convertToFormat(QImage.Format.Format_RGB32)
    width = incomingQImage.width()
    height = incomingQImage.height()
    ptr = incomingQImage.constBits()
    arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
    return arr

def qimage_to_pil_image(incomingQImage):
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    incomingQImage.save(buffer, "PNG")
    pil_img = Image.open(io.BytesIO(buffer.data()))
    return pil_img