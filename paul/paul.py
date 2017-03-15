import discord
import datetime
from discord.ext import commands
from .utils import checks
from __main__ import settings
from __main__ import send_cmd_help

class paul:

	"""Paul's custom commands!"""
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def dateJoined(self, ctx):
		"""Prints the date you joined the channel."""
		user = ctx.message.author
		if len(ctx.message.mentions) != 0:
			user = ctx.message.mentions[0]
		msg = '{} first joined the channel on '.format(user.mention) + user.joined_at.strftime("%B %d, %Y")
		await self.bot.send_message(ctx.message.channel, msg)
		
	@commands.command(pass_context=True)
	async def channelInfo(self, ctx):
		"""Prints the channel ID"""
		await self.bot.send_message(ctx.message.channel, 'ID: ' + ctx.message.channel.id)
		
	@commands.command(pass_context=True)
	async def listChannels(self, ctx):
		"""Prints a list of the channels on the server"""
		list = ctx.message.channel.server.channels
		msg = ''
		for channel in list:
			msg += '\n' + channel.name + ' '
		await self.bot.send_message(ctx.message.channel, msg)

	@commands.command(pass_context=True)
	async def spam(self, ctx, user : discord.Member):
		"""Sends 5 PMs to a user
		
		spam [user] - Bot will send 5 private messages to the specified  user (cannot spam bot or admins)."""
		msg = ''
		server = ctx.message.server
		admin_role = settings.get_server_admin(server)
		if user.id == self.bot.user.id:
			user = ctx.message.author
			msg = 'Haha, you cannot spam me!'
		elif discord.utils.get(user.roles, name=admin_role):
			user = ctx.message.author
			msg = 'Haha, you cannot spam an admin!'
		else:
			msg = 'Spam courtesy of {} :D'.format(ctx.message.author.mention)
		for x in range(0, 5):
			await self.bot.send_message(user, msg)

def setup(bot):
	n = paul(bot)
	bot.add_cog(n)
