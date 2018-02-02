import discord
import datetime
from discord.ext import commands
from __main__ import send_cmd_help

class say:

	"""Get your bot to say a message in a specified channel"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def say(self, ctx, ch : discord.Channel = None, *text):
		"""Bot says a message.
		
		say  [channel mention] [message] - Bot says a message in the specified channel
		NOTE: You must mention a channel even if that's your current channel"""
		message = "";
		for word in text:
			message += word + " "
		
		if ch is None:
			await send_cmd_help(ctx)
			#await self.bot.send_message(ctx.message.channel, message)
		else:
			await self.bot.send_message(ch, message)
			await self.bot.delete_message(ctx.message)

def setup(bot):
	n = say(bot)
	bot.add_cog(n)