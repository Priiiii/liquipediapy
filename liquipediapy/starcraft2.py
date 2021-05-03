import liquipediapy.exceptions as ex
from liquipediapy.liquipediapy import liquipediapy
import re
import unicodedata
from liquipediapy.starcraft2_modules.player import starcraft2_player
import itertools
from urllib.request import quote

class starcraft2():

	def __init__(self,appname):
		self.appname = appname
		self.liquipedia = liquipediapy(appname,'starcraft2')
		self.__image_base_url = 'https://liquipedia.net'

	def get_player_info(self,playerName,results=False):
		player_object = starcraft2_player()
		playerName = player_object.process_playerName(playerName)		
		soup,redirect_value = self.liquipedia.parse(playerName)
		if redirect_value is not None:
			playerName = redirect_value
		player = {}
		#player['info'] = player_object.get_player_infobox(soup)
		#player['links'] = player_object.get_player_history(soup)
		#player['history'] = player_object.get_player_history(soup)
		player['achivements'] = player_object.get_player_achivements(soup)
		if results:
			parse_value = playerName + "/Matches"
			try:
				soup,__ = self.liquipedia.parse(parse_value)
				player['results'] = player_object.get_player_matches(soup)
			except ex.RequestsException:
				player['results'] = []

		return player

