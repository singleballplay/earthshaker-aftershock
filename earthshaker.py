#################################################################################
##     _________    ____  ________  _______ __  _____    __ __ __________  __
##    / ____/   |  / __ \/_  __/ / / / ___// / / /   |  / //_// ____/ __ \/ /
##   / __/ / /| | / /_/ / / / / /_/ /\__ \/ /_/ / /| | / ,<  / __/ / /_/ / / 
##  / /___/ ___ |/ _, _/ / / / __  /___/ / __  / ___ |/ /| |/ /___/ _, _/_/  
## /_____/_/  |_/_/ |_| /_/ /_/ /_//____/_/ /_/_/  |_/_/ |_/_____/_/ |_(_)   
##     ___    ______________________  _____ __  ______  ________ __
##    /   |  / ____/_  __/ ____/ __ \/ ___// / / / __ \/ ____/ //_/
##   / /| | / /_    / / / __/ / /_/ /\__ \/ /_/ / / / / /   / ,<   
##  / ___ |/ __/   / / / /___/ _, _/___/ / __  / /_/ / /___/ /| |  
## /_/  |_/_/     /_/ /_____/_/ |_|/____/_/ /_/\____/\____/_/ |_|                     
##                                                     
## A P-ROC Project by Scott Danesi, Copyright 2013-2014
## Built on the PyProcGame Framework from Adam Preble and Gerry Stellenberg
#################################################################################

#################################################################################
##     __  ______    _____   __   _________    __  _________
##    /  |/  /   |  /  _/ | / /  / ____/   |  /  |/  / ____/
##   / /|_/ / /| |  / //  |/ /  / / __/ /| | / /|_/ / __/   
##  / /  / / ___ |_/ // /|  /  / /_/ / ___ |/ /  / / /___   
## /_/  /_/_/  |_/___/_/ |_/   \____/_/  |_/_/  /_/_____/   
##
#################################################################################

import procgame.game
import pinproc
import base
from base import BaseGameMode

################################################
# GLOBAL VARIABLES
################################################
gameYaml = 'config/es.yaml'
gameSettings = 'config/settings.yaml'
gameMachineType = 'wpcAlphanumeric'
ballsPerGame = 3

################################################
# GAME CLASS
################################################
class EarthshakerAftershock(procgame.game.BasicGame):
	def __init__(self, machine_type):
		super(EarthshakerAftershock, self).__init__(machine_type)
		self.load_config(gameYaml)
		self.balls_per_game = ballsPerGame
			
	def reset(self):
		super(EarthshakerAftershock, self).reset()
		#boot into Game Over Mode
		self.base_mode = BaseGameMode(game)
		self.modes.add(self.base_mode)
		
################################################
# GAME DEFINITIONS
################################################
game = EarthshakerAftershock(machine_type=gameMachineType)
game.logging_enabled=True

game.reset()
game.run_loop()