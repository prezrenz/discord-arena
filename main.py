import discord
from discord.ext import commands
import os
import arena
import battlemap
import random


if __name__ == '__main__':
	intents = discord.Intents.default()
	intents.message_content = True
	started = False
	looking = False

	bot = commands.Bot(command_prefix='//', intents=intents)
	combatants = []
	map = [[0 for i in range(10)] for j in range(10)]
	current_turn = 0
	current_round = 0

	def update_map():
		emb = discord.Embed(description=f"Current Turn:{combatants[current_turn].user.mention}\nCurrent Round:{current_round}")
		url = battlemap.get_url() + "10x10"
		for i in combatants:
			url = url + i.put_in_map()
		print(url)
		emb.set_image(url=url)
		return emb
	
	# TODO handle users with no avatar, doesnt work without avatar for now, returns error
	def add_combatant(user):
		shortcode = battlemap.get_shortcode(user.avatar.url)
		x = chr(random.randint(1, 10) + 96)
		y = random.randint(1, 10)
		invoker = combatant.Combatant(user, shortcode, x, y, map)
		combatants.append(invoker)

	def user_in_combat(user):
		for i in combatants:
			if i.user == user:
				return True

	def end_turn():
		global current_turn
		global current_round
	
		if (current_turn + 1) >= len(combatants):
			current_round += 1
			current_turn = 0
		else:
			current_turn += 1

	@bot.event
	async def on_ready():
		print(f'Logged on as {bot.user}!')

	@bot.command()
	async def start(ctx):
		global started
		global looking
		global current_round
		print(map)
	
		if not looking:
			looking = True
			add_combatant(ctx.author)
			await ctx.send("Looking for combatants...")
		
		elif looking and not started and (len(combatants) > 1):
			started = True
			looking = False
			random.shuffle(combatants)
			current_round += 1
			await ctx.send("Battle Started...",embed=update_map())
		elif len(combatants) <= 1:
			await ctx.send("Needs at least one other combatant!")
	
	@bot.command()
	async def move(ctx, x, y):
		x = int(x)
		y = int(y)
		
		if combatants[current_turn].user == ctx.author:
			if (abs(x) + abs(y)) <= combatants[current_turn].mov:
				combatants[current_turn].move(x, y, map)
				end_turn()
				await ctx.send(embed=update_map())
			else:
				await ctx.send(f"{ctx.author.mention}, you tried moving more than {combatants[current_turn].mov} squares! Please try again...")
		else:
			await ctx.send(f"{ctx.author.mention}, it's not your turn!")
	
	@bot.command()
	async def join(ctx):
		global looking
	
		if looking:
			if not user_in_combat(ctx.author) and (len(combatants) < 4):
				add_combatant(ctx.author)
				await ctx.send(f"Use {ctx.author.mention} has been added in combat.")
			else:
				await ctx.send(f"User {ctx.author.mention} already in combat, or participants already at 4!")
		else:
			await ctx.send("Match ongoing, please wait till the conclusion!")
	
	@bot.command()
	async def end(ctx):
		global started
		global looking
	
		if ctx.author.guild_permissions.administrator:
			started = False
			looking = False
			combatants.clear()
			current_turn = 0
			current_round = 0
			
			await ctx.send("Battle Ended")
		else:
			await ctx.send("Only admins are allowed to end fights!")

	bot.run(os.getenv("TOKEN"))