#=====Importing Libraries==============================#
import numpy as np
from PIL import Image
from pikepdf import Pdf, PdfImage, Name
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
#======================================================#

#======Method to Extract Images from PDF===============#
def extract_images(path):
    '''Method Extract Images from PDF
    Parameters:
    path : (String) Path of PDF File
    Returns :
    IMGS : (List) List of Image Numpy arrays'''
    pdf = Pdf.open(path)
    def get_pil_image(obj):
        img = []
        try:
            img = PdfImage(obj).as_pil_image()
            if not(img.mode in ['L','1']):
                if img.mode!='RGB':
                    imgData = np.frombuffer(img.tobytes(), dtype='B')
                    invData = np.full(imgData.shape, 255, dtype='B')
                    invData -= imgData
                    imgs = Image.frombytes(img.mode, img.size, invData.tobytes())               
                    img = imgs.convert('RGB')
            else:
                pass
        except Exception as e:
            pass
        return img
    IMGS=[]
    for k in pdf.pages:
        if len((list(k.images.keys())))!=0:
            ims = list(k.images.keys())
            ims = [k.images[i] for i in ims]
            ims = [get_pil_image(i) for i in ims]
            ims = [np.array(k) for k in ims if k!=[]]
            IMGS.extend(ims)        
    return IMGS
#========================================================#
