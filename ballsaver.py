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
##     ____  ___    __    __       _____ ___ _    ____________ 
##    / __ )/   |  / /   / /      / ___//   | |  / / ____/ __ \
##   / __  / /| | / /   / /       \__ \/ /| | | / / __/ / /_/ /
##  / /_/ / ___ |/ /___/ /___    ___/ / ___ | |/ / /___/ _, _/ 
## /_____/_/  |_/_____/_____/   /____/_/  |_|___/_____/_/ |_|  
## 
#################################################################################

import procgame.game
from procgame import *
import pinproc

#ballSaverTime = 15
#ballSaverWarningThreshold = ballSaverTime
#ballSaverTimeLeft = ballSaverTime

class BallSaver(game.Mode):
	def __init__(self, game, priority):
			super(BallSaver, self).__init__(game, priority)

			self.ballSaverTime = 15
			self.ballSaverGracePeriodThreshold = 3
			self.ballSaveLampsActive = True

	def mode_started(self):
		self.cancel_delayed('stopballsavelamps')
		self.game.utilities.set_player_stats('ballsave_active',True)
		self.ballSaveLampsActive = True
		self.update_lamps()
		
	def mode_stopped(self):
		self.cancel_delayed('stopballsavelamps')
		self.cancel_delayed('ballsaver')
		self.game.utilities.set_player_stats('ballsave_active',False)
		self.update_lamps()

	def update_lamps(self):
		if (self.game.utilities.get_player_stats('ballsave_active') == True and self.ballSaveLampsActive == True):
			self.startBallSaverLamps()
		else:
			self.stopBallSaverLamps()
		
	def startBallSaverLamps(self):
		self.game.lamps.shootAgain.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=False)

	def startBallSaverLampsWarning(self):
		self.game.lamps.shootAgain.schedule(schedule=0x0F0F0F0F, cycle_seconds=0, now=False)

	def stopBallSaverLamps(self):
		self.ballSaveLampsActive = False
		self.game.lamps.shootAgain.disable()

	def stopBallSaverMode(self):
		self.game.modes.remove(self)

	def kickBallToTrough(self):
		self.game.utilities.acCoilPulse(coilname='outholeKicker_CaptiveFlashers',pulsetime=50)

	def kickBallToShooterLane(self):
		self.game.utilities.acCoilPulse(coilname='ballReleaseShooterLane_CenterRampFlashers1',pulsetime=100)

	def saveBall(self):
		#Kick another ball
		self.game.utilities.displayText(199,topText='BALL SAVED',bottomText=' ',seconds=3,justify='center')

		#Stop Skillshot
		self.game.modes.remove(self.game.skillshot_mode)

		self.kickBallToTrough()
		self.kickBallToShooterLane()
		self.stopBallSaverMode()

	def sw_outhole_closed_for_1s(self, sw):
		self.saveBall()
		if (self.game.utilities.get_player_stats('ballsave_active') == True):
			return procgame.game.SwitchStop
		else:
			return procgame.game.SwitchContinue

	def sw_outhole_closed(self, sw):
		if (self.game.utilities.get_player_stats('ballsave_active') == True):
			return procgame.game.SwitchStop
		else:
			return procgame.game.SwitchContinue

	def sw_ballShooter_open_for_1s(self, sw):
		self.delay(name='ballsaver',delay=self.ballSaverTime,handler=self.stopBallSaverMode)
		self.delay(name='stopballsavelamps',delay=self.ballSaverTime - self.ballSaverGracePeriodThreshold,handler=self.stopBallSaverLamps)
		return procgame.game.SwitchContinue