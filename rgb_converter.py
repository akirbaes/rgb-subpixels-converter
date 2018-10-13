from __future__ import print_function
from PIL import Image
from math import ceil
from statistics import mean
import sys
"""Usage: python rgb_converter.py somesnake.gif [vscale] [r] [g] [b]
Returns: the image converted into subpixels horizontally (each three pixel goes into R, G, B)
If "vscale" is mentionned, scale vertically (average greyscale)
If r, g or b are mentionned, output with the given pixel as leftmost
Accepts gifs and pngs."""
	
filename = "ghost.gif"
try:
    filename=sys.argv[1]
except:
    print("No argument parameter given.\nUsing default filename:",filename)

sysargs = sys.argv[2:]
vscale = 0

vscale = "vscale" in sysargs

print("vscale:",("No","Yes")[vscale])
	
offsets = ("r" in sysargs, "g" in sysargs, "b" in sysargs)
if(offsets == (0,0,0)):
	offsets = (0,0,1)
	
print("Offset sets:","r (0) "*offsets[0]+"g (1) "*offsets[1]+"b (2) "*offsets[2])

x_offsets = (index for index, value in enumerate(offsets) if value==1)

def save_gif_sequence(images,outname, duration = 1000/20):
	#https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html#gif
	first = images[0].convert("P")
	rest = [image.convert("P") for image in images[1:]]
	first.save(outname, save_all=True, append_images=rest, duration = duration, loop = 0)

def load_gif_animation(gifname):
	image = Image.open(gifname)
	image.seek(0)
	try:
		while(1):
			yield image
			image.seek(image.tell() + 1)
	except EOFError:
		return

def turn_image(original, offset=0, vscale=False):
	if(offset not in (0,1,2)):
		print("Offset must be 0, 1 or 2. Risk of error.")
	yscale = (1,3)[vscale]
	
	original = original.convert("L") #Convert into grayscale
	old_width = original.size[0]
	new_width = int(ceil(float(old_width+offset)/3)) #One third, but offset possible
	old_height = original.size[1]
	new_height = int(ceil(float(old_height)/yscale)) #One third or not

	output = Image.new("RGB", (new_width,new_height))
	for y in range(new_height):
		for x in range(new_width):
			rgb = []
			for old_x in range(x*3,min(x*3+3,old_width+offset)):
				#print(old_x,y)
				if(old_x<offset):
					value = 0
				else:
					values = []
				
					for old_y in range(y*yscale,min(y*yscale+yscale,old_height)):
						values.append(original.getpixel((old_x-offset,old_y)))
					value = mean(values) #Average of the three vertical pixels
					
				#print(value)
				rgb.append(int(value))
			#print(rgb)
			if(len(rgb)!=3):
				#print("Border lost:",rgb)
				rgb+=[0]*(3-len(rgb))
			output.putpixel((x,y),tuple(rgb))
	return output
		
		
if __name__ == "__main__":
	for offset in x_offsets:
		#This way long gifs are read three times: is it a bad idea?
		result = []
		if(filename[-4:]==".gif"):
			images = load_gif_animation(filename)
		else:
			images = (Image.open(filename),)
		for image in images:
			result.append(turn_image(image,offset,vscale))
			
		name = filename[:-4] +("_tall","_small")[vscale] + "_" + "RGB"[offset]
		
		if(len(result)>1):
			save_gif_sequence(result,name+".gif")
			print("Saved",name+".gif")
		else:
			result[0].save(name+".png")
			print("Saved",name+".png")