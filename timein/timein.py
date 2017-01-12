import discord
from discord.ext import commands
import datetime
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp

class timein:
	"""Gets the current time of anywhere in the world"""

	def __init__(self, bot):
		self.bot = bot

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
		url = ''
		flag = ':flag_'
		APIKey = "Your API key here"

		if text.lower() == 'use':
			url="http://api.timezonedb.com/v2/list-time-zone?key=" + APIKey + "&format=xml&country=US&zone=*New_York*'
			flag += 'us: EAST '
		elif text.lower() == 'usw':
			url="http://api.timezonedb.com/v2/list-time-zone?key=" + APIKey + "&format=xml&country=US&zone=*Los_Angeles*'
			flag += 'us: WEST '
		elif len(text) != 2 or ' ' in text == False:
			await self.bot.say("Country code must be 2 letters and from this list https://timezonedb.com/country-codes")
			return
		else:
			if text == 'UK' or text == 'uk':
				text = 'GB'
			url="http://api.timezonedb.com/v2/list-time-zone?key=" + APIKey + "&format=xml&country=" + text
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

def setup(bot):
	if soupAvailable:
		bot.add_cog(timein(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")