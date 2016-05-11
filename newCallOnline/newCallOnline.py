import discord
from discord.ext import commands

class newCall:

	"""Alerts everyone when a user joins a voice channel if there is no one else in voice"""
	def __init__(self, bot):
		self.bot = bot
	
	async def userJoinedVoice (self, before, after):
		count = 0 # Total number of users in chat

		if after.voice_channel != None and after.is_afk != True and (before.voice_channel == None or before.is_afk == True): # Check if user was not previously in a voice channel or was in the afk channel
			if after.voice_channel != before.voice_channel: # Check if user has not just muted their mic or similar
				#if after.voice_channel != None:	# Check if user has not 
				for channel in after.server.channels:
					if channel != after.server.afk_channel:
						count += len(channel.voice_members) # Add the number of users in this voice channel
				if count == 1: # If you are the only user in the voice channels
					botRole = None
					for role in after.server.roles:
						if role.name == 'bots':
							botRole = role
							break
					members = after.server.members
					voiceMember = None
					onlineMembers = ''
					for mem in members:
						if (mem.status == discord.Status.online or mem.status == discord.Status.idle) and botRole not in mem.roles:
							if mem.voice_channel != None and mem.voice_channel != after.server.afk_channel:
								voiceMember = mem.mention
							else:
								onlineMembers += (' ' + mem.mention)
					ch = after.server.get_channel('channel ID here') #ID of general channel
					#ch = after.server.get_channel('channel ID here') #ID of general channel
					await self.bot.send_message(ch, voiceMember + ' started a new voice call' + onlineMembers)

def setup(bot):
	n = newCall(bot)
	bot.add_cog(n)
	bot.add_listener(n.userJoinedVoice, "on_voice_state_update")