"""
Tracker
Tracker implementation
"""

from simplesensor.shared.threadsafeLogger import ThreadsafeLogger
from time import time
import cv2

class Tracker():
	def __init__(self, bbox, frame, kind, moduleConfig, loggingQueue):
		""" Create and initialize a new Tracker. Set up constants and parameters. """

		if kind in ["KCF", "MIL", "MEDIANFLOW", "GOTURN", "TLD", "BOOSTING"]:
			self.tracker = cv2.Tracker_create(kind)
			self.tracker.init(frame, (bbox['x'], bbox['y'], bbox['w'], bbox['h']))
			self.created = time()
			self.bbox = (bbox['x'], bbox['y'], bbox['w'], bbox['h'])
			self.velocity = (0, 0)
			self.updateTime = self.created
			self.config = moduleConfig

			# Constants
			self._useVelocity = self.config['UseVelocity']
			self._horizontalVelocityBuffer = self.config['HorizontalVelocityBuffer']
			self._verticalVelocityBuffer = self.config['VerticalVelocityBuffer']

			# Setup logging queue
			self.logger = ThreadsafeLogger(loggingQueue, __name__)
		else:
			self.logger.error("Type %s not supported by mTracker" % kind)

	def getCreated(self):
		""" Get created time """
		return self.created

	def right(self):
		""" Get right bound of tracker """
		return self.bbox[0] + self.bbox[2]

	def top(self):
		""" Get top bound of tracker """
		return self.bbox[1] + self.bbox[3]

	def bottom(self):
		""" Get bottom bound of tracker """
		return self.bbox[1]

	def left(self):
		""" Get left bound of tracker """
		return self.bbox[0]

	def area(self):
		""" Get area of tracker bounding box """
		return abs(self.right() - self.left())*abs(self.top() - self.bottom())

	def update(self, frame):
		""" Update tracker.
		If velocity hack is being used, calculate the new velocity of the midpoint. 
		"""
		ok, bbox = self.tracker.update(frame)

		if self._useVelocity:
			# Set velocity (pixels/sec)
			deltaT = time() - self.updateTime
			centreNow = ((bbox[0]+bbox[2]/2), (bbox[1]+bbox[3]/2))
			centreLast = ((self.bbox[0]+self.bbox[2]/2), (self.bbox[1]+self.bbox[3]/2))
			Vx = (centreNow[0] - centreLast[0])/deltaT
			Vy = (centreNow[1] - centreLast[1])/deltaT
			self.velocity = (Vx, Vy)
			self.logger.debug('New velocity: %s' % str(self.velocity[0])+', '+str(self.velocity[1]))

			self.updateTime = time()

		self.bbox = bbox

		return ok, bbox

	def getProjectedLocation(self, time):
		""" Get the estimated location of the bounding box, based on previous velocity. """

		deltaT = max((time - self.updateTime), 1)
		centreNow = ((self.bbox[0]+self.bbox[2]/2), (self.bbox[1]+self.bbox[3]/2))
		projectedX = centreNow[0]+(self.velocity[0]*deltaT)
		projectedY = centreNow[1]+(self.velocity[1]*deltaT)
		return (projectedX, projectedY)

	def getVelocityBuffer(self):
		''' Another hack to improve low frame rate tracking.
		"Spread" out the bounding box based on velocity.
		'''
		return (abs(self.velocity[0])*self._horizontalVelocityBuffer,
			abs(self.velocity[1])*self._verticalVelocityBuffer)
