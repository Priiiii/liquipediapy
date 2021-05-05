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
		player['info'] = player_object.get_player_infobox(soup)
		player['links'] = player_object.get_player_history(soup)
		player['history'] = player_object.get_player_history(soup)
		player['achivements'] = player_object.get_player_achivements(soup)
		player['statistics'] = player_object.get_player_statistics(soup)
		if results:
			parse_value = playerName + "/Matches"
			try:
				soup,__ = self.liquipedia.parse(parse_value)
				player['results'] = player_object.get_player_matches(soup)
			except ex.RequestsException:
				player['results'] = []

		return player

	def get_tournaments(self,tournamentType=None):
		tournaments = []
		if tournamentType is None:
			page_val = 'Portal:Leagues'
		else:	
			page_val = tournamentType.capitalize()+'_Tournaments'				
		soup,__ = self.liquipedia.parse(page_val)
		#this splits the tables up so find_tables[0] gives the first table on the page and spits out everything within it
		find_tables = soup.find_all('div',class_="table-responsive")
		#getting the text of the heading in the tables
		rows = soup.find_all('tr')
		rows = [row for row in rows]
		header_row = rows[0]
		header_list = []
		for cell in header_row.find_all('th'):
			value = cell.get_text()
			header_list.append(value)
		#gets the cell value and it is assigned to the right heading
		for row in rows:
			tournament_row = {}
			count = 0
			cells = row.find_all('td')
			for i in range(0, len(cells)):
				value = cells[i].find(text=True, recursive=False)
				if value is None:
					value = cells[i].get_text()
					tournament_row[header_list[i]] = value
				else:
					value = value.rstrip()
					tournament_row[header_list[i]] = value
				if "Winner" in header_list[i] or "Runner-up" in header_list[i]:

					if cells[i].find("a") is not None:
						country_value = cells[i].find("a").get("title")
					else:
						country_value = None

					race_value = None
					find_zerg = cells[i].find("a", {"href": "/starcraft2/Zerg"})
					find_protss = cells[i].find("a", {"href": "/starcraft2/Protoss"})
					find_terran = cells[i].find("a", {"href": "/starcraft2/Terran"})
					if find_zerg:
						race_value = cells[i].find("a", {"href": "/starcraft2/Zerg"})["title"]
					elif find_protss:
						race_value = cells[i].find("a", {"href": "/starcraft2/Protoss"})["title"]
					elif find_terran:
						race_value = cells[i].find("a", {"href": "/starcraft2/Terran"})["title"]
					else:
						tournament_row[header_list[i]] = []	
					if cells[i].find("span", {"style": "white-space:pre"}) is not None:
						id_value = cells[i].find("span", {"style": "white-space:pre"}).get_text()
					else:
						id_value = None
					final_list = []
					final_list.append(country_value)
					final_list.append(race_value)	
					final_list.append(id_value)	
					tournament_row[header_list[i]] = final_list
			tournaments.append(tournament_row)

		return(tournaments)
				