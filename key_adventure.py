
"""
	KEY-VENTURE ( September 17, 2020 ) Raymond Brian D. Gorospe

	Key-Venture​ is a single-player dungeon-crawler game where the player 
	adventurously explores a dungeon. The objective is for the player to find the key 
	and get out of the dungeon through the door.

	The Player wins by collecting the KEY and heading to the DOOR before running out of moves. 
	The Player can only lose moves if the player moves towards any direction; Sucessful or not
	(moving into a wall), or if the player Investigates an Entity in a certain direction.

	Commands:
		H - Help 
		Q - Quit

	Movements:
		W - Move up
		A - Move Left
		S - Move Down
		D - Move Right

	Characters / Entities:
		# - Wall
		O - Player
		K - Key
		D - Door
		M - Increases Player Moves
		  - Space

"""

# Directional Movements
DIRECTIONS = {
	"W": (-1, 0),
	"S": (1, 0),
	"D": (0, 1),
	"A": (0, -1)
}

# Dungeon Layout: Max Turns
GAME_LEVELS = {
    "game1.txt": 7,     
    "game2.txt": 12,    
    "game3.txt": 19
}

# Characters / Entities:
PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

INVALID = """That's invalid."""
WIN_TEXT = "You have won the game with your strength and honour!"
LOSE_TEXT = "You have lost all your strength and honour."

def load_game(filename):
	#	Builds the level from the filename parameter.
	#	Parameters:	filename <string> - A string that represents the filenmae of the level.
	#	Returns:	list<list<string>> - Returns 2D array that represents the level structure.

	dungeon_layout = []

	with open(f'levels/{filename}', "r") as file:
		game_layout = file.readlines()

	for index in range(len(game_layout)):
		line = game_layout[index].strip('\n')
		row = []

		for i in range(len(line)):

			row.append(line[i])

		dungeon_layout.append(row)
		# print(*dungeon_layout[index]) # Display the dungeon layout

	return dungeon_layout






"""======================================

|	|	|	|	GAME LOGIC	|	|	|	|

======================================"""

class GameLogic:

	def __init__(self, dungeon_name = f'game1.txt'):
		
		self._dungeon = load_game(f'{dungeon_name}')
		self._dungeon_size = len(self._dungeon)

		self._player = Player(GAME_LEVELS[dungeon_name])

		self._game_information = self.init_game_information()

		self._win = False

		self._display = Display(self._game_information, self._dungeon_size)

	def get_dungeon_size(self):
		# Returns the size the Width of the dungeon as an integer.
		return self._dungeon_size

	def init_game_information(self) -> dict:
		# Returns a dictionary containing the position and the 
		# corresponding Entity as the keys and values respectively.
		#  This method also sets the Player’s position. 

		# Returns: <dict<tuple<int, int >: Entity>>
		
		game_information = {}
		for row, line in enumerate(self._dungeon):
			for col, char in enumerate(line):
				pos = (row, col)

				if char == Entity.get_id( self._player ):
					# This method also sets the Player’s position. 
					self._player.set_position(pos)

				elif not char == ' ':
					game_information[pos] = self.get_entity(pos)

		return game_information

	def get_game_information(self):
		# Returns a dictionary containing the position and the corresponding Entity, 
		# as the keys and values, for the current dungeon. 

		# Very similar to ( init_game_information )  in terms of function.
		return self.init_game_information()

	def get_player(self):
		# Returns the Player object within the game. 
		return Entity.get_id( self._player )

	def get_entity(self, position: tuple):
		# Returns an Entity at a given position in the dungeon.
		# Parameters: position <tuple<int, int>> - Location of Entity
		# Return: Entity

		character = self._dungeon[position[0]][position[1]]

		if character == Entity.get_id( Key() ):		return Key()
		if character == Entity.get_id( Wall() ): 	return Wall()
		if character == Entity.get_id( Door() ):	return Door()
		if character == Entity.get_id( Player(0) ):	return Player(0)
		if character == Entity.get_id( MoveIncrease() ): return MoveIncrease()

		return None

	def get_entity_in_direction(self, direction: str):
		# Returns an Entity in the given direction of the Player’s position.
		return self.get_entity(self.new_position(direction))

	def collision_check(self, direction: str) -> bool:
		# Returns ​False​ if a player can travel in the given direction, they won’t collide. ​
		# True, they will collide, otherwise
		facing = self.get_entity(self.new_position(direction))
		return facing.collidable if facing is not None else True

	def new_position(self, direction: str) -> tuple:
		# Returns a tuple of integers that represents the new position given the direction.
		# Parameters: direction <string> - Direction the player wishes to interact
		# Return: tuple<int, int>

		facing = DIRECTIONS[direction.upper()]
		player_position = self._player.get_position()

		return (facing[0] + player_position[0], facing[1] + player_position[1])

	def move_player(self, direction: str):
		# Update the Player’s position to place them one position in the given direction. 
		# Parameters: direction <string> - Direction the player wishes to interact

		if self.collision_check(direction):

			# Retrive Player Positions		
			old_pos = self._player.get_position()
			new_pos = self.new_position(direction)

			# Retrive Entity / Item in Direction
			entity = self.get_entity_in_direction(direction)

			# Does an the on_hit effect				
			if isinstance(entity, Door):
				entity.on_hit(GameLogic())


			if isinstance(entity, Items):
				entity.on_hit(GameLogic())

				self._game_information.pop(new_pos)
				self._display = Display(self._game_information, self._dungeon_size)

			# Update Map and Player Position
			self._dungeon[old_pos[0]][old_pos[1]] = ' '
			self._dungeon[new_pos[0]][new_pos[1]] = self._player._id

			self._player.set_position(new_pos)

	def check_game_over(self) -> bool:
		# Return if user has used all their moves
		return self._player.moves <= 0

	def set_win_state(self, win: bool):
		# Set the game’s win state to be True or False.
		self._win = (str(Key()) in self._player.inventory and self._player.get_position() == self.get_positions(DOOR)) or win

	def won(self) -> bool:
		# Return game’s win state.
		return self._win

	def get_positions(self, entity):
		# Returns a <list> of <tuples> containing all position of a given Entity Type.
		# Parameters: entity <string> - The ID of an Entity
		# Returns: <list<tuples<int,int>>>

		positions = []
		for row, line in enumerate(self._dungeon):
			for col, char in enumerate(line):

				if char == entity:
					positions.append((row,col))
		
		return positions






"""======================================

|	|	|	|	DISPLAY		|	|	|	|

======================================"""

class Display:

	def __init__(self, game_information, dungeon_size):
		# Constructs a view of the dungeon.
		self._game_information = game_information
		self._dungeon_size = dungeon_size

	def display_moves(self, moves):
		# Displays the number of moves the Player has left.
		# Parameters: moves <int> - The number of moves the Player can make.
		print(f'Moves left: {moves}\n')

	def display_game(self, player_pos):
		# Returns a printed display of the Dungeon
		# Parameters: player_pos tuple<int, int> - Player Position

		dungeon = ""

		for i in range(self._dungeon_size):

			rows = ""
			for k in range(self._dungeon_size):
				position = (i, k)
				entity = self._game_information.get(position)

				if position == player_pos:
					char = PLAYER
				elif entity is not None:
					char = entity.get_id()
				else:
					char = SPACE

				rows += char + ' '

			if i < self._dungeon_size - 1:
				rows += "\n"

			dungeon += rows

		print(dungeon)





"""==========================================================================================

|	|	|	|	|	|	ENTITIES/CHARACTERS [WALLS, PLAYER, DOOR]	|	|	|	|	|	|	|

=========================================================================================="""

class Entity:

	_id = 'Entity'
	name = 'Entity'	

	def get_id(self) -> str:
		# Returns a <string> that represents the Entity's ID.
		return self._id

	def set_collide(self, collidable: bool):
		# Sets collision state for the Entity.
		# Parameters:	collidable <bool> - Sets the collision state for the Entity.
		
		self.collidable = collidable

	def can_collide(self) -> bool:
		# Returns a <boolean> if whether or not the entity can be collided
		return self.collidable

	def __str__(self) -> str:
		# Shows a string representation of your object to be read easily by others.
		return str(f"{self.name}('{self._id}')")

	def __repr__(self) -> str:
		# Shows a string representation of the object.
		return str(self.name + "('" + self._id + "')")




class Wall(Entity):
	_id = WALL
	name = 'Wall'
	collidable = False # Wall should never be set to True.




class Player(Entity):
	_id = PLAYER
	name = 'Player'
	collidable = None

	inventory = []
	position = ()
	moves = 0	

	def __init__(self, moves):
		# Sets Player Turns/Moves
		self.moves = moves 

	"""----------------------
	Inventory / Items Related
	----------------------"""

	def add_item(self, item: Entity):
		# Adds the item to the Player’s Inventory. 
		self.inventory.append(item)

	def get_inventory(self):
		# Returns a list that represents the Player’s inventory. If the Player has nothing 
		# in their inventory then an empty list should be returned. 
		return self.inventory

	"""------------
	Player Position
	------------"""

	def set_position(self, position: tuple):
		# Sets the position of the Player.
		self.position = position

	def get_position(self) -> tuple:
		# Returns a tuple of ints representing the position of the Player. If the Player’s 
		# position hasn’t been set yet then this method should return None.
		return "None" if not self.position else self.position

	"""---------------------
	Player Turns / Movements
	---------------------"""

	def change_move_count(self, number: int):
		# Sets number to be added to the Player’s move count. 
		self.moves += number

	def moves_remaining(self):
		# Returns an int representing how many moves the Player has left before they run out of turns. 
		return self.moves 




class Door(Entity):
	_id = DOOR
	name = 'Door'
	collidable = True

	def on_hit(self, game: GameLogic):
		# If the Player’s inventory contains a Key Entity then this method should set the 
		# ‘game over’ state to be True. 

		if str(Key()) in game._player.inventory:
			game.set_win_state(True)
		else:
			print("You dont have the Key!")





"""======================================================================================

|	|	|	|	|	|	ENTITIES/ITEMS [KEY, MOVEINCREASE, DOOR]	|	|	|	|	|	|

======================================================================================"""

class Items(Entity):

	_id = 'Items'
	name = 'Items'

	def on_hit(self, game: GameLogic):
		raise NotImplementedError




class Key(Items):
	_id = KEY
	name = 'Key'
	collidable = True

	def on_hit(self, game: GameLogic):
		# When the player takes the Key the Key should be added to the Player’s inventory. 
		# The Key should then be removed from the dungeon once it’s in the Player’s inventory
		game._player.add_item(str(Key()))



class MoveIncrease(Items):
	_id = MOVE_INCREASE
	name = 'MoveIncrease'
	collidable = True

	MOVE_VALUE_INCREASE = 5

	def on_hit(self, game: GameLogic):
		# Returns moves the Player will be granted when they collect this Item, 
		# the default value should be 5. 
		game._player.change_move_count(self.MOVE_VALUE_INCREASE)






"""======================================

|	|	|	|	GAME APP	|	|	|	|

======================================"""

class GameApp:
	game = GameLogic()

	while not game.won():

		if game.check_game_over():
			break

		# Display the board
		game._display.display_game(game._player.position)
		game._display.display_moves(game._player.moves_remaining())

		user = input('Please Input an Action: ')

		if user.upper() in DIRECTIONS:
			game.move_player(user)
			game._player.change_move_count(-1)
		else:
			print(INVALID)

		# Missing HELP, QUIT, and INVENTORY Commands for user

	if game.won():
		print(WIN_TEXT)
	else:
		print(LOSE_TEXT)


def main():
	GameApp()

if __name__ == '__main__':
	main()