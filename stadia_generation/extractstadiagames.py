import re

with open("stadia.html", "r") as f:

	game_name_pat = re.compile('aria-label=\"View (.*?)\"')
	game_sku_pat = re.compile('data-sku-id=\"(.*?)\"')
	game_app_pat = re.compile('data-app-id=\"(.*?)\"')
	game_icon_pat = re.compile('srcset=\"(.*?)\"')

	with open("stadiagames.txt", "w+") as g:
		for line in f:
			game_name = re.search(game_name_pat, line)
			game_sku = re.search(game_sku_pat, line)
			game_app = re.search(game_app_pat, line)
			game_icon = re.search(game_icon_pat, line)
			try:
				print(game_name.group(1))
				g.write(game_name.group(1)+"\n")
			except:
				pass
			try:
				print(game_sku.group(1))
				g.write(game_sku.group(1)+"\n")
			except:
				pass
			try:
				print(game_app.group(1))
				g.write(game_app.group(1)+"\n")
			except:
				pass
			try:
				print(game_icon.group(1))
				g.write(game_icon.group(1)+"\n")
			except:
				pass
	



