import requests
from subprocess import Popen
import os

folder = os.getcwd()
print(folder)

def fetch_icon(name,icon):
	#stored as webp online
	filename = name.replace(" ", "_")+".webp"
	r = requests.get(icon)
	with open(folder+"/icons/"+filename, 'wb+') as h:
		h.write(r.content)
	return filename




with open("./stadiagames.txt", "r") as f:
	with open("./stadiapython.txt", "w+") as g:
		while True:
			name = f.readline().strip()[:-1] #strip whitespace and trailing period
			if name=="":
				break
			sku = f.readline().strip()
			app = f.readline().strip()
			icon = f.readline().strip()
			iconname = fetch_icon(name,icon)
			output= name[:-1]+","+sku+","+app+","+iconname
			print(output)
			g.write(output+"\n")
		

#resize then convert, then remove old webps. could probably be one line...
Popen(['mogrify', '-resize', '96x96', folder+'/icons/*.webp'])
Popen(['mogrify', '-format', 'png', folder+'/icons/*.webp'])
Popen(['rm', folder+'/icons/*.webp'])
