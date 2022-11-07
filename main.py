import os
from PIL import Image
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-i", "--input", help="Input image path", type=str)
parser.add_argument("-o", "--output", help="Output path", type=str)
parser.add_argument("-cw", "--cluster_width", help="Cluster width", type=int, default=1)
parser.add_argument("-ch", "--cluster_height", help="Cluster height", type=int, default=1)
parser.add_argument("-mw", "--monitor_width", help="Monitor X resolution", type=int, default=82)
parser.add_argument("-mh", "--monitor_height", help="Monitor Y resolution", type=int, default=40)

args = parser.parse_args()



clusterWidth = args.cluster_width
clusterHeight = args.cluster_height

monXResolution = args.monitor_width
monYResolution = args.monitor_height

colors = [0xF0F0F0, 0xF2B233, 0xE57FD8, 0x99B2F2, 
        0xDEDE6C, 0x7FCC19, 0xF2B2CC, 0x4C4C4C,
        0x999999, 0x4C99B2, 0xB266E5, 0x3366CC, 
        0x7F664C, 0x57A64E, 0xCC4C4C, 0x111111]

def get_palette(cs):
    palette = []
    for color in cs:
        rgb = tuple(int(hex(color).split('x')[1][i:i+2], 16) for i in (0, 2, 4))
        palette.append(rgb[0])
        palette.append(rgb[1])
        palette.append(rgb[2])
    return palette
 
def ResizeImage(size, maxWidth, maxHeight):
    ratioX = maxWidth / size[0]
    ratioY = maxHeight / size[1]
    ratio = min(ratioX, ratioY)

    #Un-comment this to prevent upscaling
    #ratio = ratio if ratio < 1 else 1

    newWidth = int(size[0] * ratio)
    newHeight = int(size[1] * ratio)

    return (newWidth, newHeight)

inputPath = args.input
imagePath = os.path.dirname(inputPath)+"\\"
imageName = os.path.basename(inputPath)

#RESIZING ORIGINAL IMAGE
img = Image.open(imagePath+imageName).convert("RGB")
size = ResizeImage(img.size, clusterWidth*monXResolution, clusterHeight*monYResolution)
resized = img.resize((size[0],size[1]), resample=Image.Resampling.LANCZOS)

print("Resized to {}".format(size))

#CONVERTING PALETTE
palette = get_palette(colors)

p_resized = Image.new('P', (16, 16))
p_resized.putpalette(palette * 16) #Total palette must be len() = 768

conv = resized.quantize(palette=p_resized, dither=0)

print("Converted to main palette")

#CROPPING TO SUB-IMAGES
images = []

yTiles = int(size[1]/monYResolution)
xTiles = int(size[0]/monXResolution)

dY = size[1]-yTiles*monYResolution
dX = size[0]-xTiles*monXResolution

xPointer = 0
yPointer = 0

for y in range(yTiles):
    for x in range(xTiles):
        images.append(conv.crop((xPointer, yPointer, xPointer + monXResolution, yPointer + monYResolution)))
        xPointer = xPointer + monXResolution
    if dX > 0:
        images.append(conv.crop((xPointer, yPointer, xPointer + dX, yPointer + monYResolution)))
    xPointer = 0
    yPointer = yPointer + monYResolution

if dY > 0:
    for x in range(xTiles):
        images.append(conv.crop((xPointer, yPointer, xPointer + monXResolution, yPointer + dY)))
        xPointer = xPointer + monXResolution
    if dX > 0:
        images.append(conv.crop((xPointer, yPointer, xPointer + dX, yPointer + dY)))

print("Cropped to {} sub-images".format(len(images)))

#CREATE CC FILES
for i, image in enumerate(images):
    with open(args.output+"\\"+str(i)+".nfp", 'w') as f:
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                pixel = image.getpixel((x,y))
                value = hex(pixel).split('x')[1]
                f.write(value)
            f.write("\n")

print("Done")