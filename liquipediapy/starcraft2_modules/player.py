import re
from urllib.request import quote
import unicodedata


class starcraft2_player():

	def __init__(self):
		self.__image_base_url = 'https://liquipedia.net'
		self.__player_exceptions = []

	def process_playerName(self,playerName):
		if playerName in self.__player_exceptions:
			playerName = playerName+"_(player)"
		if not playerName[0].isdigit():
			playerName = list(playerName)
			playerName[0] = playerName[0].upper()
			playerName = "".join(playerName)	
		playerName = quote(playerName)

		return playerName		
	
	def get_player_infobox(self,soup):
		player = {}
		try:
			image_url = soup.find('div', class_='infobox-image').find('img').get('src')		
			if 'PlayerImagePlaceholder' not in image_url:
				player['image'] = self.__image_base_url+image_url
			else:
				player['image'] = ''	
		except AttributeError:
			player['image'] = ''		

		try:	
			info_boxes = soup.find_all('div', class_='infobox-cell-2')
		except AttributeError:
			return player

		for i in range(0,len(info_boxes),2):
			attribute = info_boxes[i].get_text().replace(':','')
			if attribute == 'Country':
				player_countries = []
				countries = info_boxes[i+1].find_all('a')
				for country in countries:
					player_countries.append(country.get_text())
				player_countries = [country for country in player_countries if len(country)>0]	
				player['countries'] = player_countries
			elif attribute == 'Birth':
				player['birth_details'] = unicodedata.normalize("NFKD",info_boxes[i+1].get_text())
			elif attribute == 'Total Earnings':
				player['earnings'] = int(info_boxes[i+1].get_text().replace('$','').replace(',','').replace('.',''))
			elif attribute == 'Race':
				player['race'] = info_boxes[i+1].get_text().split(',')
			elif attribute == 'Alternate IDs':
				player['ids'] = info_boxes[i+1].get_text().split(',')
			elif attribute == 'Years Active':
				player['years_active'] = info_boxes[i+1].get_text()
			elif attribute == 'Nicknames':
				player['nicknames'] = info_boxes[i+1].get_text().split(',')
			elif attribute == 'Team':
				player['team'] = info_boxes[i+1].get_text().split(',')
			else:
				attribute = attribute.lower().replace('(', '').replace(')', '').replace(' ','_')
				player[attribute] = info_boxes[i+1].get_text().rstrip()
		return player

	def get_player_links(self,soup):
		player_links = {}
		try:		
			links = soup.find('div', class_='infobox-icons').find_all('a')
		except AttributeError:
			return player_links
		for link in links:
			link_list = link.get('href').split('.')
			site_name = link_list[-2].replace('https://','').replace('http://','')
			player_links[site_name] = link.get('href')

		return player_links	

	def get_player_history(self,soup):
		player_history = []
		histories = soup.find_all('div', class_='infobox-center')
		try:
			histories = histories[-1].find_all('div', recursive=False)
		except (IndexError,AttributeError):	
			return player_history
		for history in histories:
			teams_info = history.find_all('div')
			if len(teams_info) > 1:
				team = {}
				team['duration'] = teams_info[0].get_text()
				team['name'] = teams_info[1].get_text()
				player_history.append(team)

		return player_history

	def get_player_achivements(self,soup):
		achivements = []
		rows = soup.find_all("tr")
		for row in rows:
			try:
				attrs = {"style": "padding-left:1em;text-align:left"}
				icon = "results-team-icon"
				if len(row)>6:
					match = {}
					match["date"] = row.find("td").get_text()
					place = row.find("td", class_=re.compile("^placement")).get_text()
					match["placement"] = re.sub("[A-Za-z]", "", place)
					try:
						match["tournament"] = row.find("td", attrs).get_text()
					except AttributeError:
						match["tournament"] = row.find("td", attrs={"style": "padding-left:1em;text-align:left;"}).get_text()	
					match["team"] = row.find("span", class_="team-template-image-legacy").a["title"]
					score = row.find("td", class_="results-score").get_text()
					match["score"] = "".join(score.split())
					try:
						find_zerg = row.find("td", class_="results-team-icon").find("a", {"href": "/starcraft2/Zerg"})
						find_protoss = row.find("td", class_="results-team-icon").find("a", {"href": "/starcraft2/Protoss"})
						find_terran = row.find("td", class_="results-team-icon").find("a", {"href": "/starcraft2/Terran"})
						if find_zerg:
							match["opponent race"] = row.find("td", class_="results-team-icon").find("a", {"href": "/starcraft2/Zerg"})["title"]
						elif find_protoss:
							match["opponent race"] = row.find("td", class_="results-team-icon").find("a", {"href": "/starcraft2/Protoss"})["title"]
						elif find_terran:
							match["opponent race"] = row.find("td", class_="results-team-icon").find("a", {"href": "/starcraft2/Terran"})["title"]
						else:
							match["opponent race"] = []
					except AttributeError:
						match["opponent race"] = []
					try:
						opponent_name = row.find("td", class_="results-team-icon").find_all("a")[-1]
						if opponent_name: 
							match["opponent id"] = row.find("td", class_="results-team-icon").find_all("a")[-1]["title"]
						else:
							match["opponent id"] = []
					except:
						match["opponent id"] = []
					match["prize"] = row.find_all("td")[-1].get_text()
					achivements.append(match)
			except AttributeError:
				pass

		return achivements

	def get_player_matches(self,soup):
		matches = []
		rows = soup.find_all("tr")
		for row in rows:
			try:
				match = {}
				match["date"] = row.find("td").get_text()
				match["tier"] = row.find_all("td")[2].find("a").get_text()
				match["tournament"] = row.find_all("td")[4].get_text()
				score = []
				for i in range(5,8):
					score.append(row.find_all("td")[i].get_text())
				match["score"] = " ".join(str(x) for x in score)
				try:
					find_country = row.find_all("td")[8].find("span").find("a", {"href": re.compile("/starcraft2/Category:*")})
					if find_country:
						match["opponent country"] = row.find_all("td")[8].find("a")["title"]
					else:
						match["opponent country"] = []
				except AttributeError:
					match["opponent country"] = []
				try:
					find_zerg = row.find_all("td")[8].find("a", {"href": "/starcraft2/Zerg"})
					find_protss = row.find_all("td")[8].find("a", {"href": "/starcraft2/Protoss"})
					find_terran = row.find_all("td")[8].find("a", {"href": "/starcraft2/Terran"})
					if find_zerg:
						match["opponent race"] = row.find_all("td")[8].find("a", {"href": "/starcraft2/Zerg"})["title"]
					elif find_protss:
						match["opponent race"] = row.find_all("td")[8].find("a", {"href": "/starcraft2/Protoss"})["title"]
					elif find_terran:
						match["opponent race"] = row.find_all("td")[8].find("a", {"href": "/starcraft2/Terran"})["title"]
					else:
						match["opponent race"] = []
				except AttributeError:
					match["opponent race"] = []
				match["opponent id"] = row.find_all("td")[8].find_all("a")[-1].get_text()
				matches.append(match)
			except AttributeError:
				pass	

		return matches

	def get_player_statistics(self,soup):
		stats = []
		toss_win_loss = []
		terran_win_loss = []
		zerg_win_loss = []
		random_win_loss = []

		attrs = {"style": "margin-top:0;text-align:center"}
		matchup = {}

		check_protoss = soup.find("table", attrs).find("tr", class_="Protoss")
		if check_protoss:
			for i in range(0,10):
				if i % 2 != 0:
					protoss_stats = soup.find("table", attrs).find("tr", class_="Protoss").find_all("td")[i].get_text()
					toss_win_loss.append(protoss_stats)

			matchup["protoss v protoss"] = toss_win_loss[0]
			matchup["protoss v terran"] = toss_win_loss[1]
			matchup["protoss v zerg"] = toss_win_loss[2]
			matchup["protoss v random"] = toss_win_loss[3]
			matchup["total protoss win - loss"] = toss_win_loss[4]

		check_terran = soup.find("table", attrs).find("tr", class_="Terran")
		if check_terran:
			for i in range(0,10):
				if i % 2 != 0:
					terran_stats = soup.find("table", attrs).find("tr", class_="Terran").find_all("td")[i].get_text()
					terran_win_loss.append(terran_stats)

			matchup["terran v protoss"] = terran_win_loss[0]
			matchup["terran v terran"] = terran_win_loss[1]
			matchup["terran v zerg"] = terran_win_loss[2]
			matchup["terran v random"] = terran_win_loss[3]
			matchup["total terran win - loss"] = terran_win_loss[4]	

		check_zerg = soup.find("table", attrs).find("tr", class_="Zerg")
		if check_zerg:
			for i in range(0,10):
				if i % 2 != 0:
					zerg_stats = soup.find("table", attrs).find("tr", class_="Zerg").find_all("td")[i].get_text()
					zerg_win_loss.append(zerg_stats)

			matchup["zerg v protoss"] = zerg_win_loss[0]
			matchup["zerg v terran"] = zerg_win_loss[1]
			matchup["zerg v zerg"] = zerg_win_loss[2]
			matchup["zerg v random"] = zerg_win_loss[3]
			matchup["total zerg win - loss"] = zerg_win_loss[4]	
		
		check_random = soup.find("table", attrs).find("tr", class_="Random")
		if check_random:
			for i in range(0,10):
				if i % 2 != 0:
					random_stats = soup.find("table", attrs).find("tr", class_="Random").find_all("td")[i].get_text()
					random_win_loss.append(random_stats)

			matchup["random v protoss"] = random_win_loss[0]
			matchup["random v terran"] = random_win_loss[1]
			matchup["random v zerg"] = random_win_loss[2]
			matchup["random v random"] = random_win_loss[3]
			matchup["total random win - loss"] = random_win_loss[4]

		stats.append(matchup)
		return stats
		

