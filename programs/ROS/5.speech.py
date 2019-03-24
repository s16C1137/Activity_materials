#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import rospy
import numpy as np
from geometry_msgs.msg import Twist

class openjtalk(object):
	def __init__(self):
		self._sub_nearlistball = rospy.Subscriber('/ball_xy1', Twist, self._callback_speech)
		self._pub_ballxy = rospy.Publisher('/ball_xy', Twist, queue_size=1)

		self.dic = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
		self.htsvoice = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"
		self.speed = 1.0
		self._info = np.zeros(4, dtype = 'int64')
		self._color = np.zeros(2, dtype = 'unicode')

	def _owari(self):
		text = '、おわります' 
		self.speak(text)
		

	def speak(self, text):
		command = "echo '{0}'".format(text)
		command += " | open_jtalk -x {0} -m {1} -r {2} -ow /dev/stdout".format(self.dic, self.htsvoice, self.speed)
		command += " | aplay"
		os.system(command)

	def _callback_speech(self, message):
		self._info[0] = message.linear.x*10
		self._info[1] = message.linear.z
		self._info[3] = message.angular.x
		self._info[2] = message.angular.z 
		if (self._info[3] == 1):
			self._info[0] = self._info[0] - 30
		elif(self._info[0] > 1000 or self._info[0] < -1000):
			self._owari()
		else:	
			if(self._info[1] == 1):
				self._color[0] = u'あ'
				self._color[1] = u'か'		
			elif(self._info[1] == 2):
				self._color[0] = u'あ'
				self._color[1] = u'お'
			elif(self._info[1] == 3):		
				self._color[0] = u''
				self._color[1] = u'き'	

			self._speech()
			self._arduino()


	def _speech(self): 
		print self._color[0]
		print self._color[1]
		print self._info[2]
		print self._info[0]

		if(self._info[2]>=0 and self._info[0]>=0):
			text = '%s%sいろ、 %dど、 %dみり' %(self._color[0].encode('utf-8'), self._color[1].encode('utf-8') , self._info[2], self._info[0])
		elif(self._info[2]<0 and self._info[0]>=0):
			text = '%s%sいろ、 まいなす%dど、 %dみり' %(self._color[0].encode('utf-8'), self._color[1].encode('utf-8') , self._info[2]*(-1), self._info[0])
		elif(self._info[2]>0 and self._info[0]<0):
			text = '%s%sいろ、%dど、まいなす%dみり' %(self._color[0].encode('utf-8'), self._color[1].encode('utf-8'),self._info[2], self._info[0]*(-1))
		elif(self._info[2]<=0 and self._info[0]<0):
			text = '%s%sいろ、まいなす%dど、まいなす%dみり' %(self._color[0].encode('utf-8'), self._color[1].encode('utf-8'),self._info[2]*(-1), self._info[0]*(-1))
		self.speak(text)

	def _arduino(self):
		ball_xy = Twist()
		ball_xy.linear.x = self._info[0]*0.1
		ball_xy.linear.z = self._info[1]
		ball_xy.angular.z = self._info[2]
		self._pub_ballxy.publish(ball_xy)

if __name__ == '__main__':
	print "start"
	rospy.init_node('speech')
	talker = openjtalk()
	try:
		rospy.spin()
	except KeyboardInterrupt:
		pass
