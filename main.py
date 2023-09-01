import discord
from discord.ext import commands
import os
import arena
import battlemap
import random


if __name__ == '__main__':
	intents = discord.Intents.default()
	intents.message_content = True

	bot = commands.Bot(command_prefix='//', intents=intents)
	started = False
	looking = False
	combatants = []
	map = [[0 for i in range(10)] for j in range(10)]
	current_turn = 0
	current_round = 0

	def update_map():
		emb = discord.Embed(description=f"Current Turn:{combatants[current_turn].user.mention}\nCurrent Round:{current_round}\nCurrent Actions Left:{combatants[current_turn].act}")
		url = battlemap.get_url() + "10x10"
		for i in combatants:
			url = url + i.put_in_map()
		emb.set_image(url=url)
		return emb
	
	# TODO handle users with no avatar, doesnt work without avatar for now, returns error
	def add_combatant(user):
		shortcode = battlemap.get_shortcode(user.avatar.url)
		x = chr(random.randint(1, 10) + 96)
		y = random.randint(1, 10)
		invoker = arena.Combatant(user, shortcode, x, y, map)
		combatants.append(invoker)

	def user_in_combat(user):
		for i in combatants:
			if i.user == user:
				return True

	async def set_win(ctx):
		started = False
		looking = False
		current_turn = 0
		current_round = 0
		
		await ctx.send(f"{ctx.author.mention} has won!", embed=update_map())
		await ctx.send("Battle Ended...")
		combatants.clear()

	def check_actions_left():
		if combatants[current_turn].act > 1:
			combatants[current_turn].act -= 1
		else:
			combatants[current_turn].act -= 1
			end_turn()

	def end_turn():
		global current_turn
		global current_round
	
		if (current_turn + 1) >= len(combatants):
			current_round += 1
			current_turn = 0
			for i in combatants:
				i.reset_action()
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
				check_actions_left()
				await ctx.send(embed=update_map())
			else:
				await ctx.send(f"{ctx.author.mention}, you tried moving more than {combatants[current_turn].mov} squares! Please try again...")
		else:
			await ctx.send(f"{ctx.author.mention}, it's not your turn!")
	
	@bot.command()
	async def attack(ctx, dir):
		if combatants[current_turn].user == ctx.author:
			attacker = combatants[current_turn]
			target = [0, 0]
			match dir:
				case "up":
					attacker_pos = attacker.get_position()
					target[0] = attacker_pos[0]
					target[1] = attacker_pos[1] - 1

				case "down":
					attacker_pos = attacker.get_position()
					target[0] = attacker_pos[0]
					target[1] = attacker_pos[1] + 1

				case "left":
					attacker_pos = attacker.get_position()
					target[0] = attacker_pos[0] - 1
					target[1] = attacker_pos[1]

				case "right":
					attacker_pos = attacker.get_position()
					target[0] = attacker_pos[0] + 1
					target[1] = attacker_pos[1]

				case _:
					await ctx.send("Invalid direction, please use 'up', 'down', 'left', or 'right'")
					return
			
			for i in combatants:
				if i.get_position() == target:
					i.hp -= 2
					check_actions_left()
					
					for i in combatants:
						if i.hp <= 0:
							combatants.remove(i)
					if len(combatants) <= 1:
						await ctx.send(f"{ctx.author.mention} hit {i.user.mention} for 2 damage!", embed=update_map())
						await set_win(ctx)
					else:
						await ctx.send(f"{ctx.author.mention} hit {i.user.mention} for 2 damage!", embed=update_map())
					return
			
			await ctx.send("no target in that direction")
		else:
			await ctx.send(f"{ctx.author.mention}, it's not your turn!")

	@bot.command()
	async def join(ctx):
		global looking
	
		if looking:
			if not user_in_combat(ctx.author) and (len(combatants) < 4):
				add_combatant(ctx.author)
				await ctx.send(f"User {ctx.author.mention} has been added in combat.")
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