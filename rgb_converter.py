from __future__ import print_function
from PIL import Image
from math import ceil
from statistics import mean
import sys
print("""Usage: python rgb_converter.py somesnake.gif [vscale] [r] [g] [b] [combine] [reverse] [colored|greyscale]
Returns: the image converted into subpixels horizontally (each three pixel goes into R, G, B)
If "vscale" is mentionned, scale vertically (average greyscale)
If r, g or b are mentionned, output with the given pixel as leftmost
Accepts gifs and pngs.\n----\n""")
	
filename = "ghost.gif"
try:
    filename=sys.argv[1]
except:
    print("No argument parameter given.\nUsing default filename:",filename)

sysargs = sys.argv[2:]

vscale = "vscale" in sysargs
combine = "combine" in sysargs
offsets = ("r" in sysargs, "g" in sysargs, "b" in sysargs)
if(offsets == (0,0,0)):
	offsets = (1,0,0) #default: no offset
x_offsets = [index for index, value in enumerate(offsets) if value==1]
#List with some out of 0,1,2

reverse = "reverse" in sysargs
forward = not reverse
colored = (not "greyscale" in sysargs) and (not "grayscale" in sysargs)

if("reverse" in sysargs):
	print("Subpixels to full image")
	print("vscale:",("No","Yes")[vscale])
	print("colored output:",("No","Yes")[colored])
else:
	print("Greyscale image to subpixels")
	print("vscale:",("No","Yes")[vscale])
	print("Offset sets:","r (0) "*offsets[0]+"g (1) "*offsets[1]+"b (2) "*offsets[2])


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

def turn_image_into_subpixels(original, offset=0, vscale=False):
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
		
def turn_subpixels_into_image(original, colored=True, vscale = True):
	original = original.convert('RGB')
	yscale = (1,3)[vscale]
	old_width = original.size[0]
	new_width = old_width * 3 
	old_height = original.size[1]
	new_height = old_height * yscale
	
	output = Image.new("RGB", (new_width,new_height))
		
	for x_old in range(old_width):
		for y_old in range(old_height):
			r,g,b = tuple(original.getpixel((x_old,y_old)))
			x_new = x_old*3
			y_new = y_old*yscale
			for i, value in enumerate((r,g,b)):
				for j in range(yscale):
					if(colored):
						color = [0,0,0]
						color[i] = value
					else:
						color = [value,value,value]
						
					output.putpixel((x_new+i,y_new+j),tuple(color))
	return output
	
def output_images(images, outname):
	if(len(images)>1):
		print("Outputing",len(images),"images")
		save_gif_sequence(images,outname+".gif")
		print("Saved",outname+".gif")
	elif(len(images)==1):
		images[0].save(outname+".png")
		print("Saved",outname+".png")
	else:
		return 0
	
if __name__ == "__main__":
	print("----\n")
	#Load image(s)
	if(filename[-4:]==".gif"):
		print("Loading animation")
		images = load_gif_animation(filename)
	else:
		images = (Image.open(filename),)
	
	if(forward):
		#Turn image into subpixels
		results = [[],[],[]]
		for image in images:
			for offset in x_offsets:
				output_image = turn_image_into_subpixels(image,offset,vscale)
				results[offset].append(output_image)
		if(not combine):
			for offset,result in enumerate(results):
				name = filename[:-4]+".subpixels"+("_tall","_small")[vscale] + "_" + "RGB"[offset]
				output_images(result,name)
		elif(combine):
			result = results[0]+results[1]+results[2]
			name = filename[:-4]+".subpixels"+("_tall","_small")[vscale] + "_" + "R"*offsets[0] + "G"*offsets[1] + "B"*offsets[2]
			output_images(result,name)		
	elif(reverse):
		#Return subpixels into image
		result = []
		for image in images:
			result.append(turn_subpixels_into_image(image,colored,vscale))
		name = filename[:-4]+".fullpixels"+("_low","_full")[vscale] + "_" + ("grayscale","color")[colored]
		output_images(result,name)