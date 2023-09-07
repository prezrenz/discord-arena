import discord
from discord.ext import commands
import os
import arena
import battlemap
import random
import helpers

weapons_data = [
	{"name": "fist", "damage": 1, "range": 1},
	{"name": "dagger", "damage": 2, "range": 1},
	{"name": "rapier", "damage": 3, "range": 1},
	{"name": "axe", "damage": 3, "range": 1},
	{"name": "spear", "damage": 2, "range": 2},
]

if __name__ == '__main__':
	intents = discord.Intents.default()
	intents.message_content = True

	bot = commands.Bot(command_prefix='//', intents=intents)
	started = False
	looking = False
	combatants = []
	weapons = []
	map = [[0 for i in range(10)] for j in range(10)]
	current_turn = 0
	current_round = 0

	def update_map():
		emb = discord.Embed(description=f"Current Turn:{combatants[current_turn].user.mention}\nCurrent Round:{current_round}\nCurrent Actions Left:{combatants[current_turn].act}\nEquipped:{combatants[current_turn].equip['name']}")
		url = battlemap.get_url() + "10x10"
		# for i in combatants:
			# url = url + i.put_in_map()
		# for i in weapons:
			# url = url + i.put_in_map()
		
		for i in map:
			for j in i:
				if j != 0:
					url = url + j.put_in_map()
		
		emb.set_image(url=url)
		return emb
	
	# TODO handle users with no avatar, doesnt work without avatar for now, returns error
	def add_combatant(user):
		shortcode = battlemap.get_shortcode(user.avatar.url)
		x = chr(random.randint(1, 10) + 96)
		y = random.randint(1, 10)
		invoker = arena.Combatant(user, shortcode, x, y, map)
		combatants.append(invoker)

	def generate_weapons():
		generate = 4
		
		while generate > 0:
			x = random.randint(1, 10)
			y = random.randint(1, 10)
			data = weapons_data[random.randint(1, len(weapons_data)-1)]
			if map[x-1][y-1] == 0:
				weapons.append(arena.Weapon(data,  x, y, map))
				generate -= 1

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
			
			current_turn = 0
			current_round = 0
			
			random.shuffle(combatants)
			generate_weapons()
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
			print("attacking")
			attacker = combatants[current_turn]
			attacker_pos = attacker.get_position()
			
			target = 0
			x_off = 0
			y_off = 0
			
			match dir:
				case "up":
					x_off = 0
					y_off = -1
				case "down":
					x_off = 0
					y_off = 1
				case "left":
					x_off = -1
					y_off = 0
				case "right":
					x_off = 1
					y_off = 0
				case _:
					await ctx.send("Invalid direction, please use 'up', 'down', 'left', or 'right'")
					return
			
			for i in range(1, attacker.equip['range'], 1):
				print(f"i is {i}")
				fx = helpers.clamp(attacker_pos[0]+(x_off*i), 1, 10)
				fy = helpers.clamp(attacker_pos[1]+(y_off*i), 1, 10)
				map_target = map[fx-1][fy-1]
				
				if map_target != 0:
					print(f"object found at {fx-1},{fy-1}")
					if isinstance(map_target, arena.Combatant):
						target = map_target
						print(f"target found {target.user.mention}")
			
			if target == 0:
				await ctx.send("No target in that direction!")
			else:
				target.hp -= attacker.equip['damage']
				check_actions_left()
				await ctx.send(f"{ctx.author.mention} hit {target.user.mention} for {attacker.equip['damage']} damage!", embed=update_map())
			
			for i in combatants:
				if i.hp <= 0:
					combatants.remove(i)
			
			if len(combatants) <= 1:
				await set_win(ctx)
			
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
			weapons.clear()
			
			await ctx.send("Battle Ended")
		else:
			await ctx.send("Only admins are allowed to end fights!")

	bot.run(os.getenv("TOKEN"))