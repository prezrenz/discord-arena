def clamp(num, min, max):
	return min if num < min else max if num > max else num
		
class Combatant():
	def __init__(self, user, shortcode, x, y, map):
		self.user = user
		self.x = x
		self.y = y
		self.mov = 4
		self.act = 2
		self.hp = 4
		x_num = ord(self.x) - 96
		map[int(x_num) - 1][self.y - 1] = self
		
		self.shortcode = shortcode
	
	def get_position(self):
		return [ord(self.x) - 96, self.y]
	
	def reset_action(self):
		self.act = 2
		self.mov = 4
	
	def put_in_map(self):
		return f"/{self.x}{self.y}~{self.shortcode}"
	
	def move(self, x, y, map):
		map[(ord(self.x) - 96 - 1)][self.y - 1] = 0
		
		
		self.y += int(y)
		x_num = ord(self.x) - 96
		x_num += int(x)
		x_num =clamp(x_num, 1, 10)
		
		self.x = chr(x_num + 96)
		self.y = clamp(self.y, 1, 10)
		
		map[(ord(self.x) - 96 - 1)][self.y - 1] = self

class  Weapon():
	def __init__(self, name, damage, range, x, y, map):
		self.name = name
		self.damage = damage
		self.range = range
		self.x = chr(x + 96)
		self.y = y
		
		map[x-1][y-1] = self
	
	def put_in_map(self):
		return f"/{self.x}{self.y}-{self.name}"

class GameState():
	def __init__(self):
		self.started = False
		self.looking = False
		self.combatants = []
		self.map = [[0 for i in range(10)] for j in range(10)]
		self.current_turn = 0
		self.current_round = 0