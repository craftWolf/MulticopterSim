'''
  Python Multicopter class

  Uses UDP sockets to communicate with MulticopterSim

  Copyright(C) 2019 Simon D.Levy

  MIT License
'''

from threading import Thread
import socket
import numpy as np

class Multicopter(object):
    '''
    Represents a Multicopter object communicating with MulticopterSim via UDP socket calls.
    '''

    def __init__(self, host='127.0.0.1', motorPort=5000, telemetryPort=5001, motorCount=4):
        '''
        Creates a Multicopter object.
        host - name of host running MulticopterSim
        motorPort - port over which this object will send motor commands to host
        telemeteryPort - port over which this object will receive telemetry  from host
        motorCount - number of motors in vehicle running in simulator on host
        '''
     
        self.motorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.motorSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        self.telemSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.telemSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        self.telemSocket.bind((host, telemetryPort))

        self.host = host
        self.motorPort = motorPort
        self.motorCount = motorCount

        self.thread = Thread(target=self._run)
        self.thread.daemon = True

        self.motorVals = np.zeros(motorCount)
        self.state = np.zeros(11)

        self.ready = False

    def start(self):
        '''
        Begins communication with simulator running on host.
        '''

        self.thread.start()

    def isReady(self):
        
        return self.ready

    def getState(self):
        '''
        Returns current vehicle state as an array of the form [time, gx, gy, gz, ax, ay, az, px, py, pz],
        where g=gyro; a=accelerometer; p=position.
        '''

        return self.state

    def setMotors(self, motorVals):
        '''
        Sets motor values between 0 and 1.
        '''
 
        self.motorVals = np.copy(motorVals)

    def _run(self):

        while True:

            data, _ = self.telemSocket.recvfrom(80)
            self.state = np.frombuffer(data)

            self.ready = True

            if self.state[0] < 0:
                self.motorSocket.close()
                self.telemSocket.close()
                break

            self.motorSocket.sendto(np.ndarray.tobytes(self.motorVals), (self.host, self.motorPort))

