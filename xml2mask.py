import numpy as np
import xml.etree.ElementTree as et
import re, os, glob
from tqdm import tqdm
import tifffile, cv2
from openslide import OpenSlide

'''
lack operation that check if wsi_fns match xml_fns
'''

wsi_load_dir = ...
xml_load_dir = ...

wsi_fns = sorted(glob.glob(wsi_load_dir + '*.mrxs'))
xml_fns = sorted(glob.glob(xml_load_dir + '*.xml'))

level = 4

def xml2mask(xml_fn, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    factor = pow(2, level)
    
    tree = et.parse(xml_fn)
    root = tree.getroot()
    regions = root.findall('Annotations/Annotation')
    for i, region in enumerate(regions):
        points = []
        for point in region.findall('Coordinates/Coordinate'):
            x = int(point.attrib['X'].split('.')[0]) 
            y = int(point.attrib['Y'].split('.')[0]) 
            y //= factor
            x //= factor
            points.append([x, y])
        pts = np.asarray([points], dtype = np.int32)
        # print(pts)
        cv2.fillPoly(img=mask, pts=pts, color=255)
    return mask
    
def save_mask(save_dir, xml_fn, shape):
    mask_id = os.path.basename(xml_fn).split('.')[0]
    save_path = os.path.join(save_dir, f'{mask_id}_l4_tumor.tif')
    mask = xml2mask(xml_fn, shape)
    tifffile.imsave(save_path, mask, compress=9)
    
def load_wsi_shape(wsi_fn, level):
    wsi_image = OpenSlide(wsi_fn)
    return wsi_image.level_dimensions[level][::-1]

if __name__=='__main__':
    save_dir = ...
    for wsi_fn, xml_fn in tqdm(zip(wsi_fns, xml_fns), total=len(wsi_fns)):
        shape = load_wsi_shape(wsi_fn, level=4)
        save_mask(save_dir, xml_fn, shape)