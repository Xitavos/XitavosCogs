import discord
from discord.ext import commands
import datetime
import os
from .utils.dataIO import fileIO
import aiohttp
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False

class timein:
	"""Gets the current time of anywhere in the world"""

	def __init__(self, bot):
		self.bot = bot
		self.settings = fileIO("data/timein/settings.json", "load")

	@commands.command()
	async def timein(self, text):
		"""Gets all current dates and times from all timezones in the specified country.
		
		Usage: timein [AA]
		
		where [AA] is a country code from this list https://timezonedb.com/country-codes
		
		Preset shortcuts:
		UK - United Kingdom (converts to GB)
		USE - United States East (New York)
		USW - United States West (Los Angeles)		
		"""
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return
		
		url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml'
		flag = ':flag_'

		if text.lower() == 'use':
			url += '&country=US&zone=*New_York*'
			flag += 'us: EAST '
		elif text.lower() == 'usw':
			url += '&country=US&zone=*Los_Angeles*'
			flag += 'us: WEST '
		elif len(text) != 2 or ' ' in text == False:
			await self.bot.say("Country code must be 2 letters and from this list https://timezonedb.com/country-codes")
			return
		else:
			if text == 'UK' or text == 'uk':
				text = 'GB'
			url += '&country=' + text
			flag += text.lower() + ': '
			
		async with aiohttp.get(url) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser")
		message = ''
		
		zones = soupObject.find_all('zone')
		for zone in zones:
			newmessage = flag
			newmessage += zone.find('countryname').get_text() + '\n'
			newmessage += zone.find('zonename').get_text() + '\n'
			unixtime = zone.find('timestamp').get_text()
			time = datetime.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')
			newmessage += time + '\n'
			message += newmessage + '\n'
		
		await self.bot.say(message)
		
def check_folders():
	if not os.path.exists("data/timein"):
		print("Creating data/timein folder...")
		os.makedirs("data/timein")

def check_files():
	settings = {"api_key": "Get your API key from: https://timezonedb.com"}
	
	f = "data/timein/settings.json"
	if not fileIO(f, "check"):
		print("Creating settings.json")
		print("You must obtain an API key as noted in the newly created 'settings.json' file")
		fileIO(f, "save", settings)

def setup(bot):
	check_folders()
	check_files()
	if soupAvailable:
		bot.add_cog(timein(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")