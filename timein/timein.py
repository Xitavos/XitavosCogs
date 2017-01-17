import discord
from discord.ext import commands
import datetime
import os
from .utils.dataIO import fileIO
from __main__ import send_cmd_help
import aiohttp
import time
import calendar
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
		self.favourites = fileIO("data/timein/favourites.json", "load")
		self.cache = fileIO("data/timein/cache.json", "load")

	@commands.group(pass_context=True)
	async def timein(self, ctx):
		"""Gets the date and time of a city/country"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)

	@timein.command(name="country")
	async def _timein_country(self, text):
		"""Get time using country code
		
		Usage: timein country [AA]
		
		where [AA] is a 2 letter country code from this list https://timezonedb.com/country-codes or a custom shortcut code
		
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
		elif text.lower() == 'test':
			url += '&zone=*auckland*'
			flag += 'nz: '
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
		
		status = soupObject.find('status').get_text()
		if status != 'OK':
			message += 'Request failed. Details:\n```'
			message += status + '\n'
			message += soupObject.find('message').get_text()
			message += '```\nMake sure country code is from the list at https://timezonedb.com/country-codes'
		else:
			zones = soupObject.find_all('zone')
			for zone in zones:
				newmessage = ''
				newmessage += flag
				newmessage += zone.find('countryname').get_text() + '\n'
				newmessage += zone.find('zonename').get_text() + '\n'
				unixtime = zone.find('timestamp').get_text()
				prettyTime = datetime.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')
				newmessage += prettyTime + '\n'
				message += newmessage + '\n'
		
		await self.bot.say(message)


	@timein.command(name="city")
	async def _timein_city(self, *, text):
		"""Get time by searching for a city.
		
		Usage: timein city [CITY NAME]
		
		Only capitals and other major cities are in this list
		"""
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return
		
		url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml'
		
		city = text.replace(' ', '_')
		
		url += '&zone=*' + city + '*'
		
		async with aiohttp.get(url) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser")
		message = ''
		
		status = soupObject.find('status').get_text()
		if status != 'OK':
			message += 'Request failed. Details:\n```'
			message += status + '\n'
			message += soupObject.find('message').get_text()
			message += '```\nTry searching for a capital or other major city'
		else:
			zones = soupObject.find_all('zone')
			for zone in zones:
				newmessage = ''
				newmessage += ':flag_' + zone.find('countrycode').get_text().lower() + ': '
				newmessage += zone.find('countryname').get_text() + '\n'
				newmessage += zone.find('zonename').get_text() + '\n'
				unixtime = zone.find('timestamp').get_text()
				prettyTime = datetime.datetime.utcfromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')				
				newmessage += prettyTime + '\n'
				message += newmessage + '\n'
		
		await self.bot.say(message)

	@timein.command(name="fav")
	async def _timein_fav(self, text):
		"""Display all the times you have set in your favourites
		"""
		
		lastRefresh = int(self.cache['last_refresh'])
		currentTime = int(time.time())
		if lastRefresh - currentTime > 48*60*60: #2 days
			await self.bot.say("Cache refresh in progress")
			#self.refresh_cache(self)
			
		utcTime = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
			
		favourite = self.cache['favourite']
		
		favSplit = favourite.strip().split(',')
		
		message = ''
		
		for fav in favSplit:		
			msgSplit = fav.strip().split('~')
			
			message += msgSplit[0]
			
			localTime = utcTime + int(msgSplit[1])
			prettyTime = datetime.datetime.utcfromtimestamp(int(localTime)).strftime('%Y-%m-%d %H:%M:%S')
			
			message += prettyTime + '\n\n'
			
		await self.bot.say(message)
		
	
	async def refresh_cache(self):
		tasknum = 0
		num_zones = 0
		base_msg = "Gathering data. This may take a few seconds"
		status = ' %d/%d timezones fetched' % (tasknum, num_zones)
		msg = await self.bot.say(base_msg + status)
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return
		
		favourites = self.favourites['favourite'] #need to get the name to allow multiple favourite lists
		
		finalMessage = ''
		
		split = favourites.strip().split(',')
		
		num_zones = len(split)
		status = status = ' %d/%d timezones fetched' % (tasknum, num_zones)
		msg = await self._robust_edit(msg, base_msg + status)
		
		for fav in split:
			tasknum += 1

			url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml' + fav
		
			async with aiohttp.get(url) as response:
				soupObject = BeautifulSoup(await response.text(), "html.parser")
			message = ''
			
			status = soupObject.find('status').get_text()
			if status != 'OK':
				message += 'Request failed. Details:\n```'
				message += status + '\n'
				message += soupObject.find('message').get_text()
			else:
				zones = soupObject.find_all('zone')
				for zone in zones:
					newmessage = ''
					newmessage += ':flag_' + zone.find('countrycode').get_text().lower() + ': '
					newmessage += zone.find('countryname').get_text() + '\n'
					newmessage += zone.find('zonename').get_text() + '\n'
					unixtime = zone.find('timestamp').get_text()
					prettyTime = datetime.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')
					newmessage += prettyTime + '\n'
					message += newmessage + '\n'
			finalMessage += message
			
			status = status = ' %d/%d timezones fetched' % (tasknum, num_zones)
			msg = await self._robust_edit(msg, base_msg + status)
			
			if tasknum != num_zones:
				time.sleep(2)
		await self._robust_edit(msg, finalMessage)
	
	@timein.command(name="dev")
	async def _timein_dev(self):
		"""Prints an example of what the api returns
		"""
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return

		url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml&country=GB'
		async with aiohttp.get(url) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser")
		await self.bot.say(soupObject)
		
	async def _robust_edit(self, msg, text):
		try:
			msg = await self.bot.edit_message(msg, text)
		except discord.errors.NotFound:
			msg = await self.bot.send_message(msg.channel, text)
		except:
			raise
		return msg

def check_folders():
	if not os.path.exists("data/timein"):
		print("Creating data/timein folder...")
		os.makedirs("data/timein")

def check_files():
	settings = {"api_key" : "Get your API key from: https://timezonedb.com",}
	favourites = {}
	cache = {"last_refresh" : "0", "fav" : "test",}
	
	f = "data/timein/settings.json"
	if not fileIO(f, "check"):
		print("Creating settings.json")
		print("You must obtain an API key as noted in the newly created 'settings.json' file")
		fileIO(f, "save", settings)
	f = "data/timein/favourites.json"
	if not fileIO(f, "check"):
		print("Creating favourites.json")
		fileIO(f, "save", favourites)
	f = "data/timein/cache.json"
	if not fileIO(f, "check"):
		print("Creating cache.json")
		fileIO(f, "save", cache)

def setup(bot):
	check_folders()
	check_files()
	if soupAvailable:
		bot.add_cog(timein(bot))
	else:
		raise RuntimeError("You need to run pip3 install beautifulsoup4")
