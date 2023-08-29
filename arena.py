def clamp(num, min, max):
	return min if num < min else max if num > max else num
		
class Combatant():
	def __init__(self, user, shortcode, x, y, map):
		self.user = user
		self.x = x
		self.y = y
		self.mov = 4
		x_num = ord(self.x) - 96
		print(x_num)
		map[int(x_num)][self.y] = self
		
		self.shortcode = shortcode
	
	def put_in_map(self):
		return f"/{self.x}{self.y}~{self.shortcode}"
	
	def move(self, x, y, map):
		print(map)
		map[(ord(self.x) - 96)][self.y] = 0
		
		
		self.y += int(y)
		x_num = ord(self.x) - 96
		x_num += int(x)
		x_num =clamp(x_num, 1, 10)
		
		self.x = chr(x_num + 96)
		self.y = clamp(self.y, 1, 10)
		
		map[(ord(self.x) - 96)][self.y] = self
		print(map)