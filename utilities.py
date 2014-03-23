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
##    __  ______________    _________________________
##   / / / /_  __/  _/ /   /  _/_  __/  _/ ____/ ___/
##  / / / / / /  / // /    / /  / /  / // __/  \__ \ 
## / /_/ / / / _/ // /____/ /  / / _/ // /___ ___/ / 
## \____/ /_/ /___/_____/___/ /_/ /___/_____//____/  
## 
## This mode will be used to house all the global functions that will be used
## throughout the Aftershock project.
#################################################################################

import procgame.game
from procgame import *
import pinproc
import locale
import logging
import math

import player
from player import *

class UtilitiesMode(game.Mode):
	def __init__(self, game, priority):
			super(UtilitiesMode, self).__init__(game, priority)
			##############################
			#### Set Global Variables ####
			##############################
			self.currentDisplayPriority = 0	
			self.ACCoilInProgress = False
			self.ACNameArray = []
			self.ACNameArray.append('outholeKicker_CaptiveFlashers')
			self.ACNameArray.append('ballReleaseShooterLane_CenterRampFlashers1')
			self.ACNameArray.append('dropReset_CenterRampFlashers2')
			self.ACNameArray.append('californiaFault_CenterRampFlashers3')
			self.ACNameArray.append('ejectHole_CenterRampFlashers4')
			self.ACNameArray.append('bottomBallPopper_RightRampFlashers1')
			self.ACNameArray.append('knocker_RightRampFlashers2')


	#######################
	#### Log Functions ####
	#######################
	def log(self,text,level='info'):
		if (level == 'error'):
			logging.error(text)
		elif (level == 'warning'):
			logging.warning(text)
		else:
			logging.info(text)
		print level + " - " + text


	#################################
	#### Ball Location Functions ####
	#################################
	def troughIsFull(self): #should be moved globally
		if (self.game.switches.trough1.is_active()==True and self.game.switches.trough2.is_active()==True and self.game.switches.trough3.is_active()==True):
			return True
		else:
			return False

	def releaseStuckBalls(self):
		#Checks for balls in locks or outhole and kicks them out
		if self.game.switches.outhole.is_active()==True and self.game.tiltStatus == 0: #Exception for when in tilt
			self.game.utilities.acCoilPulse(coilname='outholeKicker_CaptiveFlashers',pulsetime=50)
		if self.game.switches.ejectHole5.is_active()==True:
			self.game.utilities.acCoilPulse(coilname='ejectHole_CenterRampFlashers4',pulsetime=50)
		if self.game.switches.ballPopperBottom.is_active()==True:
			self.game.utilities.acCoilPulse(coilname='bottomBallPopper_RightRampFlashers1',pulsetime=50)
		if self.game.switches.ballPopperTop.is_active()==True:
			self.game.coils.topBallPopper.pulse(50) #Does not need AC Relay logic
		if self.game.switches.ballShooter.is_active()==True:
			self.game.coils.autoLauncher.pulse(100) #Does not need AC Relay logic

	def launch_ball(self):
		if self.game.switches.ballShooter.is_active()==True:
			self.game.coils.autoLauncher.pulse(100)

	def setBallInPlay(self,ballInPlay=True):
		self.previousBallInPlay = self.get_player_stats('ball_in_play')
		if (ballInPlay == True and self.previousBallInPlay == False):
			self.set_player_stats('ball_in_play',True)
			self.stopShooterLaneMusic()
		elif (ballInPlay == False and self.previousBallInPlay == True):
			self.set_player_stats('ball_in_play',False)

	############################
	#### AC Relay Functions ####
	############################
	def ACRelayEnable(self):
		self.game.coils.acSelect.enable()
		self.ACCoilInProgress = False

	def acCoilPulse(self,coilname,pulsetime=50):
		### Setup variables ###
		self.ACCoilInProgress = True
		self.acSelectTimeBuffer = .3
		self.acSelectEnableBuffer = (pulsetime/1000)+(self.acSelectTimeBuffer*2)

		### Remove any scheduling of the AC coils ###
		for item in self.ACNameArray:
			self.game.coils[item].disable()

		### Start the pulse process ###
		self.cancel_delayed(name='acEnableDelay')
		self.game.coils.acSelect.disable()
		self.delay(name='coilDelay',event_type=None,delay=self.acSelectTimeBuffer,handler=self.game.coils[coilname].pulse,param=pulsetime)
		self.delay(name='acEnableDelay',delay=self.acSelectEnableBuffer,handler=self.ACRelayEnable)

	def acFlashPulse(self,coilname,pulsetime=50):
		if (self.ACCoilInProgress == False or coilname not in self.ACNameArray):
			self.game.coils[coilname].pulse(pulsetime)
		else:
			#Should this try again or just cancel?
			#cannot since the delay function does not allow me to pass more than 1 parameter :(
			pass

	def acFlashSchedule(self,coilname,schedule,cycle_seconds,now=True):
		if (self.ACCoilInProgress == False or coilname not in self.ACNameArray):
			self.game.coils[coilname].disable()
			self.game.coils[coilname].schedule(schedule=schedule, cycle_seconds=cycle_seconds, now=now)
		else:
			#Should this try again or just cancel?
			#cannot since the delay function does not allow me to pass more than 1 parameter :(
			pass

	
	###########################
	#### Display Functions ####
	###########################
	def displayText(self,priority,topText=' ',bottomText=' ',seconds=2,justify='left',topBlinkRate=0,bottomBlinkRate=0):
		# This function will be used as a very basic display prioritizing helper
		# Check if anything with a higher priority is running
		if (priority >= self.currentDisplayPriority):
			self.cancel_delayed('resetDisplayPriority')
			self.game.alpha_score_display.cancel_script()
			self.game.alpha_score_display.set_text(topText,0,justify)
			self.game.alpha_score_display.set_text(bottomText,1,justify)
			self.delay(name='resetDisplayPriority',event_type=None,delay=seconds,handler=self.resetDisplayPriority)
			self.currentDisplayPriority = priority

	def resetDisplayPriority(self):
		self.currentDisplayPriority = 0
		self.updateBaseDisplay()

	def updateBaseDisplay(self):
		print "Update Base Display Called"
		if (self.currentDisplayPriority == 0 and self.game.tiltStatus == 0 and self.game.ball <> 0):
			self.p = self.game.current_player()
			self.game.alpha_score_display.cancel_script()
			self.game.alpha_score_display.set_text(locale.format("%d", self.p.score, grouping=True),0,justify='left')
			self.game.alpha_score_display.set_text(self.p.name.upper() + "  BALL "+str(self.game.ball),1,justify='right')
			print self.p.name
			print "Ball " + str(self.game.ball)
	
	######################
	#### GI Functions ####
	######################
	def disableGI(self):
		self.game.coils.giUpper.enable()
		self.game.coils.giLower.enable()
		self.game.coils.giBackbox.enable()

	def enableGI(self):
		self.game.coils.giUpper.disable()
		self.game.coils.giLower.disable()
		self.game.coils.giBackbox.disable()


	###################################
	#### Music and Sound Functions ####
	###################################
	def stopShooterLaneMusic(self):
		if (self.game.shooter_lane_status == 1):
			self.game.sound.stop_music()
			self.game.sound.play_music('main',loops=-1)
			self.game.shooter_lane_status = 0


	##########################
	#### Player Functions ####
	##########################
	def set_player_stats(self,id,value):
		if (self.game.ball <> 0):
			self.p = self.game.current_player()
			self.p.player_stats[id]=value

	def get_player_stats(self,id):
		if (self.game.ball <> 0):
			self.p = self.game.current_player()
			return self.p.player_stats[id]
		else:
			return False

	def score(self, points):
		if (self.game.ball <> 0): #in case score() gets called when not in game
			self.p = self.game.current_player()
			self.p.score += points
			# Update the base display with the current players score
			self.cancel_delayed('updatescore')
			self.delay(name='updatescore',delay=0.05,handler=self.game.utilities.updateBaseDisplay)	

	def currentPlayerScore(self):
		if (self.game.ball <> 0): #in case score() gets called when not in game
			self.p = self.game.current_player()
			return self.p.score
		else:
			return 0

	##########################
	#### Shaker Functions ####
	##########################
	def shakerPulseLow(self):
		self.game.coils.quakeMotor.pulsed_patter(on_time=5,off_time=25,run_time=255)

	def shakerPulseMedium(self):
		self.game.coils.quakeMotor.pulsed_patter(on_time=15,off_time=15,run_time=255)

	def shakerPulseHigh(self):
		self.game.coils.quakeMotor.pulse(255)

	###############################
	#### Backbox LED Functions ####
	###############################
	def setBackboxLED(self,r=0,g=0,b=0,pulsetime=0,schedule=0x00000000):
		#Global Constants
		self.totalResolutionMS = 10
		self.divisor = 255 / self.totalResolutionMS
		#Check for Reset
		if(r==0 and g==0 and b==0):
			self.game.coils.backboxLightingR.disable()
			self.game.coils.backboxLightingG.disable()
			self.game.coils.backboxLightingB.disable()
			return
		#RED Color Evaluation
		self.rOn = math.floor(r/self.divisor)
		self.rOff = self.totalResolutionMS - self.rOn
		if(self.rOn == self.totalResolutionMS):
			if(pulsetime == 0):
				self.game.coils.backboxLightingR.enable()
			else:
				self.game.coils.backboxLightingR.pulse(pulsetime)
		elif(self.rOn == 0):
			self.game.coils.backboxLightingR.disable()
		else:
			if(pulsetime == 0):
				self.game.coils.backboxLightingR.patter(self.rOn,self.rOff)
			else:
				self.game.coils.backboxLightingR.pulsed_patter(self.rOn,self.rOff,run_time=pulsetime)
		#GREEN Color Evaluation
		self.gOn = math.floor(g/self.divisor)
		self.gOff = self.totalResolutionMS - self.gOn
		if(self.gOn == self.totalResolutionMS):
			if(pulsetime == 0):
				self.game.coils.backboxLightingG.enable()
			else:
				self.game.coils.backboxLightingG.pulse(pulsetime)
		elif(self.gOn == 0):
			self.game.coils.backboxLightingG.disable()
		else:
			if(pulsetime == 0):
				self.game.coils.backboxLightingG.patter(self.gOn,self.gOff)
			else:
				self.game.coils.backboxLightingG.pulsed_patter(self.gOn,self.gOff,run_time=pulsetime)
		#BLUE Color Evaluation
		self.bOn = math.floor(b/self.divisor)
		self.bOff = self.totalResolutionMS - self.bOn
		if(self.bOn == self.totalResolutionMS):
			if(pulsetime == 0):
				self.game.coils.backboxLightingB.enable()
			else:
				self.game.coils.backboxLightingB.pulse(pulsetime)
		elif(self.bOn == 0):
			self.game.coils.backboxLightingB.disable()
		else:
			if(pulsetime == 0):
				self.game.coils.backboxLightingB.patter(self.bOn,self.bOff)
			else:
				self.game.coils.backboxLightingB.pulsed_patter(self.bOn,self.bOff,run_time=pulsetime)


