import discord
from discord.ext import commands
import datetime
import os
from .utils.dataIO import dataIO
from .utils import checks
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
		self.settings = dataIO.load_json("data/timein/settings.json")
		self.favourites = dataIO.load_json("data/timein/favourites.json")
		self.cache = dataIO.load_json("data/timein/cache.json")

	@commands.group(pass_context=True)
	async def timein(self, ctx):
		"""Gets the date and time of a city/country"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)

	@timein.command(name="country")
	async def _timein_country(self, country_code):
		"""Get time using country code
		
		country_code is a 2 letter country code from this list https://timezonedb.com/country-codes or a custom shortcut code
		
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

		if country_code.lower() == 'use':
			url += '&country=US&zone=*New_York*'
			flag += 'us: EAST '
		elif country_code.lower() == 'usw':
			url += '&country=US&zone=*Los_Angeles*'
			flag += 'us: WEST '
		elif country_code.lower() == 'test':
			url += '&zone=*auckland*'
			flag += 'nz: '
		elif len(country_code) != 2 or ' ' in country_code == False:
			await self.bot.say("Country code must be 2 letters and from this list https://timezonedb.com/country-codes")
			return
		else:
			if country_code == 'UK' or country_code == 'uk':
				country_code = 'GB'
			url += '&country=' + country_code
			flag += country_code.lower() + ': '
			
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
	async def _timein_city(self, *, city_name):
		"""Get time by searching for a city.
		
		Only capitals and other major cities are in this list
		"""
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return
		
		url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml'
		
		city = city_name.replace(' ', '_')
		
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
	
	@timein.command(name="create")
	async def _timein_create(self, timezones, *, favourite_name):
		"""Creates a favourite group of timezones that can be quickly accessed
		
		Format the timezones input as follows:
		
		 - Copy exactly (including the _ and /) the Region/City that appears when you request for the time. E.g. Europe/London
		 
		 - Separate each timezone you want in the favourite with a comma
		 
		 - Add a space then write the name of the favourite. Can be multiple words 

		 Final command should look like:
		 
		 timein create Europe/London,America/North_Dakota/New_Salem myFavourite
		"""
		
		if favourite_name in self.cache:
			await self.bot.say("Favourite with that name already exists. Editing coming soon! TM")
			return
			
		tasknum = 0
		num_zones = 0
		base_msg = "Checking and adding timezones,"
		status = ' %d/%d timezones checked' % (tasknum, num_zones)
		other = ''
		msg = await self.bot.say(base_msg + status + other)
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return
		
		timezonesList = timezones.strip().split(',')
		
		num_zones = len(timezonesList)
		
		timezonesToAdd = ''
		message = ''
		
		for timezone in timezonesList:
			url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml&zone=' + timezone
			
			async with aiohttp.get(url) as response:
				soupObject = BeautifulSoup(await response.text(), "html.parser")
			status = soupObject.find('status').get_text()
			
			tasknum += 1
			
			if status != 'OK':
				newMessage = ''
				newMessage += 'Request failed. Details:\n```'
				newMessage += status + '\n'
				newMessage += soupObject.find('message').get_text()
				newMessage += '```\nTimezone ' + timezone + ' not found, please fix'
				await self.bot.say(newMessage)
				return
			else:
				newMessage = ''
				zone = soupObject.find('zone') #zone names are unique so should only ever be one result
				newMessage += ':flag_' + zone.find('countrycode').get_text().lower() + ': '
				newMessage += zone.find('countryname').get_text() + '\n'
				newMessage += zone.find('zonename').get_text() + '\n'
				newMessage += '~' + zone.find('gmtoffset').get_text()
				message += newMessage
				timezonesToAdd += timezone
				
				if tasknum != num_zones:
					timezonesToAdd += ','
					message += ','
				
				other += "\nTimezone " + timezone + " added OK"
				await self._robust_edit(msg, base_msg + status + other)
			status = status = ' %d/%d timezones checked' % (tasknum, num_zones)
			await self._robust_edit(msg, base_msg + status + other)
			if tasknum != num_zones:
				time.sleep(2)

		self.cache[favourite_name] = message
		f = "data/timein/cache.json"
		dataIO.save_json(f, self.cache)
		self.favourites[favourite_name] = timezonesToAdd
		f = "data/timein/favourites.json"
		dataIO.save_json(f, self.favourites)
		
		base_msg = 'Favourite \"' + favourite_name + '\" successfully created\n'
		await self._robust_edit(msg, base_msg + status + other)


	@timein.command(name="delete")
	async def _timein_delete(self, *, favourite_name):
		"""Deletes a favourite group of timezones
		"""
		
		if favourite_name not in self.cache:
			await self.bot.say("Favourite with that name does not exist")
			return
			
		self.favourites.pop(favourite_name, None)
		self.cache.pop(favourite_name, None)
		
		f = "data/timein/cache.json"
		dataIO.save_json(f, self.cache)
		f = "data/timein/favourites.json"
		dataIO.save_json(f, self.favourites)
		
		await self.bot.say("Favourite \"" + favourite_name + "\" deleted")
		
	@timein.command(name="list")
	async def _timein_list(self):
		"""Lists all favourite groups of timezones
		"""
		
		message = 'Favourites\n```Name: Timezones\n'
		
		for fav in self.favourites:
			message += fav + ': '
			message += self.favourites[fav].replace(',', ', ').replace('_', ' ') + '\n'
		
		message += '```'
		await self.bot.say(message)
	
	@timein.command(name="fav")
	async def _timein_fav(self, *, favourite_name):
		"""Display all the times you have set in your favourites
		"""
		
		lastRefresh = int(self.cache['last_refresh'])
		currentTime = int(time.time())
		
		if (currentTime - lastRefresh) > 48*60*60: #2 days
			await self.refresh_cache()
			
		utcTime = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
		
		if favourite_name not in self.cache:
			await self.bot.say("Favourite does not exist")
			return
			
		favourite = self.cache[favourite_name]
		
		favSplit = favourite.strip().split(',')
		
		message = '**' + favourite_name + '**\n'
		
		for fav in favSplit:
			msgSplit = fav.strip().split('~')
			
			message += msgSplit[0]
			
			localTime = utcTime + int(msgSplit[1])
			prettyTime = datetime.datetime.utcfromtimestamp(int(localTime)).strftime('%Y-%m-%d %H:%M:%S')
			
			message += prettyTime + '\n\n'
			
		await self.bot.say(message)
		
		
	@timein.command(name="refresh")
	@checks.admin_or_permissions(administrator=True)
	async def _timein_refresh(self):
		"""Refresh the favourites cache
		
			Use if daylight saving has started/ended or if times are wrong. Takes a short while to complete, depending on how many favourites you have
		"""
		
		await self.refresh_cache()

	async def refresh_cache(self):
		tasknum = 0
		num_zones = 0
		base_msg = "Cache refreshing. This may take a few seconds..."
		status = ' %d/%d timezones fetched' % (tasknum, num_zones)
		msg = await self.bot.say(base_msg + status)
		
		apiKey = self.settings['api_key']
		if ".com" in apiKey:
			await self.bot.say("You have to set your API key, see data/timein/settings.json for details")
			return
			
		for group in self.favourites:
			message = ''
			items = self.favourites[group].strip().split(',')
			
			num_zones += len(items)
			
			status = status = ' %d/%d timezones fetched' % (tasknum, num_zones)
			await self._robust_edit(msg, base_msg + status)
			
			for item in items:
				tasknum += 1
				newMessage = ''
				url = 'http://api.timezonedb.com/v2/list-time-zone?key=' + apiKey + '&format=xml&zone=' + item
				async with aiohttp.get(url) as response:
					soupObject = BeautifulSoup(await response.text(), "html.parser")
				status = soupObject.find('status').get_text()
				if status != 'OK':
					newMessage += 'Request failed. Details:\n```'
					newMessage += status + '\n'
					newMessage += soupObject.find('message').get_text()
					newMessage += '```\nTimezone not found'
				else:
					zone = soupObject.find('zone') #zone names are unique so should only ever be one result
					newMessage += ':flag_' + zone.find('countrycode').get_text().lower() + ': '
					newMessage += zone.find('countryname').get_text() + '\n'
					newMessage += zone.find('zonename').get_text() + '\n'
					newMessage += '~' + zone.find('gmtoffset').get_text()
					if tasknum != num_zones:
						newMessage += ','
				message += newMessage
				status = status = ' %d/%d timezones fetched' % (tasknum, num_zones)
				msg = await self._robust_edit(msg, base_msg + status)
				time.sleep(2)
			self.cache[group] = message
		await self._robust_edit(msg, "Completed, " + status)

		self.cache['last_refresh'] = str(int(time.time()))
		f = "data/timein/cache.json"
		dataIO.save_json(f, self.cache)
		

	
	@timein.command(name="dev")
	@checks.admin_or_permissions(administrator=True)
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
	settings = {"api_key" : "Get your API key from: https://timezonedb.com"}
	favourites = {}
	cache = {"last_refresh" : "0"}
	
	f = "data/timein/settings.json"
	if not dataIO.is_valid_json(f):
		print("Creating settings.json")
		print("You must obtain an API key as noted in the newly created 'settings.json' file")
		dataIO.save_json(f, settings)
	f = "data/timein/favourites.json"
	if not dataIO.is_valid_json(f):
		print("Creating favourites.json")
		dataIO.save_json(f, favourites)
	f = "data/timein/cache.json"
	if not dataIO.is_valid_json(f):
		print("Creating cache.json")
		dataIO.save_json(f, cache)

def setup(bot):
	check_folders()
	check_files()
	if soupAvailable:
		bot.add_cog(timein(bot))
	else:
		raise RuntimeError("You need to run pip3 install beautifulsoup4")
