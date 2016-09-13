import discord
from discord.ext import commands

class newCall:

	"""Alerts everyone when a user joins a voice channel if there is no one else in voice"""
	def __init__(self, bot):
		self.bot = bot
	
	async def userJoinedVoice (self, before, after):
		count = 0 # Total number of users in chat

		if before.voice_channel == None or before.is_afk == True: # Check if user was not previously in a voice channel or was in the afk channel
			if after.voice_channel != before.voice_channel: # Check if user has not just muted their mic or similar
				#if after.voice_channel != None:	# Check if user has not 
				for channel in before.server.channels:
					if channel != before.server.afk_channel:
						count += len(channel.voice_members) # Add the number of users in this voice channel
				if count == 1: # If you are the only user in the voice channels
					ch = after.server.get_channel('121894777817006084') #ID of general channel
					await self.bot.send_message(ch, 'New voice call started @everyone')

def setup(bot):
	n = newCall(bot)
	bot.add_cog(n)
	bot.add_listener(n.userJoinedVoice, "on_voice_state_update")