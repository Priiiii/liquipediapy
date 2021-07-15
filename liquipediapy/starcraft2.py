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
		#getting the text from the headings of the table
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
				#if the heading is winner or runner-up extract the three elements within that cell and put them in a list
				if "Winner" in header_list[i] or "Runner-up" in header_list[i]:
					if cells[i].find("a") is not None:
						id_value = cells[i].find("a").get("title")
					else:
						id_value = None
						
					if cells[i].find("span", {"class":"flag"}):
						country_value = cells[i].find("img").get("title")
					else:
						country_value = None

					find_zerg = cells[i].find("img", {"src":"/commons/images/thumb/e/e4/Zerg_race_icon.png/17px-Zerg_race_icon.png"})
					find_protoss = cells[i].find("img", {"src":"/commons/images/thumb/0/0f/Protoss_race_icon.png/17px-Protoss_race_icon.png"})
					find_terran = cells[i].find("img", {"src":"/commons/images/thumb/1/1e/Terran_race_icon.png/17px-Terran_race_icon.png"})

					race_value = None
					if find_zerg:
						race_value = "Zerg"
					if find_protoss:
						race_value = "Protoss"
					if find_terran:
						race_value = "Terran"

					final_list = []
					final_list.append(id_value)
					final_list.append(race_value)
					final_list.append(country_value)		
					tournament_row[header_list[i]] = final_list
				if "Series" in header_list[i]:
					if cells[i].find("a") is not None:
						tournament_row[header_list[i]] = cells[i].find("a", {"href":  re.compile("/starcraft2/*")}).get("title")
					else:
						tournament_row[header_list[i]] = None
				if "Tier" in header_list[i]:
					if cells[i].find("a") is not None:
						tournament_row[header_list[i]] = cells[i].find("a").get_text()
					else:
						tournament_row[header_list[i]] = None
			tournaments.append(tournament_row)
		return(tournaments)

	def get_statistics(self,statisticsYear = None):
		tournaments = []
		if statisticsYear is None:
			page_val = "Portal:Statistics"
		else:
			page_val = 'Statistics/'+statisticsYear
		soup,__ = self.liquipedia.parse(page_val)
		find_tables = soup.find_all('div',class_="table-responsive")
		rows = soup.find_all('tr')
		rows = [row for row in rows]

		