#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2016 Joseph Muller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ROS stuff
import rospy

# XeThru Python Driver
from XeThru_Python_Driver import xethru
from XeThru_Python_Driver.xethru_const import *

# Messages
import XeThru_Resp # TODO: Add msgs to pkg
from std_msgs.msg import Header

# A few vars
global sensor, log

# when ROS say we gotta get outta here...
def shutdown():
    global sensor, log
    print 'closing Xethru'
    del sensor
    if log:
        log.close()

if __name__ == '__main__':
  # initialize this node
  rospy.init_node('xethru', anonymous=True)
  rospy.on_shutdown(shutdown)
  rate = rospy.Rate(1) # 1 Hz = 1 message/second

  # initialize the sensor
  sensor = xethru.Xethru(
               rospy.get_param('resp_port', '/dev/ttyUSB0'),
               XTS_ID_APP_RESP,
               detection_zone_min = 0.5,
               detection_zone_max = 1.2,
               led_mode = XT_UI_LED_MODE_FULL,
               verbose = True,
           )

  # logging vars
  log = rospy.get_param('log', False)
  log_format = 'Counter;StateCode;StateData;Movement;Distance;SignalQuality'

  # create a publisher on this node at topic 'resp'
  resp_pub = rospy.Publisher('resp', XeThru_Resp, queue_size=1)
  # initialize the message to send
  resp_msg = XeThru_Resp()
  resp_msg.header.seq = 1

  # create log file
  if log:
      from datetime import datetime
      log = open('XethruLog ' + str(datetime.now()) + '.txt', 'w')
      log.write(log_format + '\n')
      print 'LOGGING!'

  # main loop
  tries = 5
  while not rospy.is_shutdown():
    # check if the sensor is initialized before reading
    if sensor.is_initialized():

      # read from sensor
      status = sensor.check_status()

      # if received valid data
      if len(status) > 0 :
        # populate the message with data
        #for key in status:
        #  resp_msg[key] = status[key]
        resp_msg.Counter = status['Counter']
        resp_msg.StateCode = status['StateCode']
        resp_msg.StateData = status['StateData']
        resp_msg.Distance = status['Distance']
        resp_msg.Movement = status['Movement']
        resp_msg.SignalQuality = status['SignalQuality']

        # update the header
        resp_msg.header.seq += 1
        resp_msg.header.stamp = rospy.Time.now()

        # print our status
        m = ''
        for key in status:
          m += '(' + str(key) + ', ' + str(status[key]) + ') '
        print m

        # log our status
        if log:
            l = ';'.join([str(status[key]) for key in log_format.split(';')]) + '\n'
            log.write(l)

        # publish our message
        resp_pub.publish(resp_msg)
      # endif len(status) > 0
    else:
      print 'Sensor not intialized. Waiting ' + str(tries) + ' more times'
      if (tries < 1):
        break;

      tries -= 1

    # take a lil nap ros
    rate.sleep();
    # endif initialized
  # end main loop
  print 'XeThru done ;~)'
# endif __main__
