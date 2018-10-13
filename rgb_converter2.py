from __future__ import print_function
from PIL import Image
from math import ceil
from statistics import mean
"""Usage: python rgb_converter.py somesnake.gif
Returns: the image converted into subpixels horizontally (each three pixel goes into R, G, B)
For PNGs, a gif of the three offsets and three images of the offsets
For GIFs, three gifs of the three offsets"""
	
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
		
def main_for_png(filename):
	original = Image.open(filename)
	results = []
	for i in range(3):
		res = turn_image(original,i)
		res.save(filename+"_"+"rgb"[i]+".png")
		results.append(res)
	save_gif_sequence(results+[results[1]],filename+"_rgb.gif",1000/4)

def main_for_gif(filename):
	results_r = []
	results_g = []
	results_b = []
	for image in load_gif_animation(filename):
		results_r.append(turn_image(image,0))
		results_g.append(turn_image(image,1))
		results_b.append(turn_image(image,2))
	save_gif_sequence(results_r,filename+"_r.gif")
	save_gif_sequence(results_g,filename+"_g.gif")
	save_gif_sequence(results_b,filename+"_b.gif")
	#save_gif_sequence(results_r+results_g+results_b+results_g,"snake_rgbmove.gif")
	
	
	
def main():
	from sys import argv
	if(len(argv)==1):
		argv.append("ghost3x.gif")
	if(argv[1][-4:]==".gif"):
		main_for_gif(argv[1])
	else:
		main_for_png(argv[1])
	
def old_main():
	original = Image.open("skull.png")
	print(original.format, original.size, original.mode)
	results = []
	for i in range(3):
		res = turn_image(original,i)
		#res.show()
		res.save("_skull_"+"rgb"[i]+".png")
		results.append(res)
	save_gif_sequence(results+[results[1]],"_skull_rgb.gif",1000/4)
	
	results_r = []
	results_g = []
	results_b = []
	for image in load_gif_animation("somesnake.gif"):
		results_r.append(turn_image(image,0))
		results_g.append(turn_image(image,1))
		results_b.append(turn_image(image,2))
	save_gif_sequence(results_r,"snake_r.gif")
	save_gif_sequence(results_r+results_g+results_b+results_g,"snake_rgbmove.gif")
	
	
	
def turn_image(original, offset=0):
	if(offset not in (0,1,2)):
		print("Offset must be 0, 1 or 2. Risk of error.")
	original = original.convert("L") #Convert into grayscale
	old_width = original.size[0]
	new_width = int(ceil((old_width+2)/3.0)) #One third, but offset possible
	old_height = original.size[1]
	new_height = int(ceil(old_height/3.0)) #One third

	output = Image.new("RGB", (new_width,new_height))
	for y in range(new_height):
		for x in range(new_width):
			rgb = []
			for old_x in range(x*3,min(x*3+3,old_width)):
				#print(old_x,y)
				if(old_x<offset):
					value = 0
				else:
					values = []
				
					for old_y in range(y*3,min(y*3+3,old_height)):
						values.append(original.getpixel((old_x-offset,old_y)))
					value = mean(values) #Average of the three vertical pixels
					
				#print(value)
				rgb.append(int(value))
			#print(rgb)
			if(len(rgb)!=3):
				rgb.extend([0]*(3-len(rgb)))
			output.putpixel((x,y),tuple(rgb))
	return output
		
		
if __name__ == "__main__":
	main()