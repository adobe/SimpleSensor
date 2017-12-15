"""
Multi tracker implementation - with some tricks to make low frame rate work a bit better
author: MaX EdeLL
date: 13/37/2017
"""
from tracker import Tracker
from threadsafeLogger import ThreadsafeLogger
from time import time

class MultiTracker(object):
	def __init__(self, kind="KCF", moduleConfig=None, loggingQueue=None):
		""" Create an initialize new MultiTracker. Set up constants and parameters. """

		self.config = moduleConfig
		self.trackers = []  # List of trackers
		self.kind = kind
		self.focus = None
		self.loggingQueue = loggingQueue

		# Constants
		self._useVelocity = self.config['UseVelocity']
		self._closestThreshold = self.config["ClosestThreshold"]
		self._primaryTarget = self.config['PrimaryTarget']

		# Setup logging queue
		self.logger = ThreadsafeLogger(loggingQueue, __name__)

	def add(self, bbox, frame, kind="KCF"):
		""" Add new tracker with default type KCF. """
		aTracker = Tracker(bbox, frame, kind, self.config, self.loggingQueue)
		self.trackers.append(aTracker)

	def removeAt(self, i):
		""" Remove Tracker at index i. """
		self.trackers.pop(i)

	def remove(self, aTracker):
		""" Remove tracker provided as parameter. """
		self.trackers.remove(aTracker)

	def update(self, frame):
		""" Loop through each tracker updating bounding box, keep track of failures. """

		bboxes = []
		ind = 0
		failed = []
		for aTracker in self.trackers:
			ok, bbox = aTracker.update(frame)
			if not ok:
				failed.append(ind)
			else:
				bboxes.append(bbox)
			ind += 1
		if len(failed) == 0:
			return True, bboxes, None
		else:
			self.logger.error('Failed to update all trackers')
			return False, bboxes, failed

	def clear(self):
		""" Remove all trackers. """
		self.trackers.clear()
		self.focus = None

	def bboxContainsPt(self, bbox, pt, vBuffer):
		""" Check if bbox contains pt. 
		Optionally provide velocity buffer to spread containing space. 
		"""
		if ((bbox['x']-vBuffer[0] <= pt[0] <= (bbox['x']+bbox['w']+vBuffer[0])) and
			(bbox['y']-vBuffer[1] <= pt[1] <= (bbox['y']+bbox['h']+vBuffer[1]))
			):
			return True
		else:
			return False

	def projectedLocationMatches(self, tracker, bbox):
		""" Check if the velocity of the tracker could put it in the same spot as the bbox. """
		if tracker.velocity:
			return self.bboxContainsPt(bbox, tracker.getProjectedLocation(time()), tracker.getVelocityBuffer())
		else:
			return False

	def intersects(self, tracker, bbox):
		""" Check if the bbox and the trackers bounds intersect. """
		if (tracker.right()<bbox['x']
			or bbox['x']+bbox['w']<tracker.left()
			or tracker.top()<bbox['y']
			or bbox['y']+bbox['h']<tracker.bottom()
			):
				return False # intersection is empty
		else:
			return True # intersection is not empty

	def contains(self, bbox):
		""" Check if the MultiTracker already has a tracker for the object detected. 
		Uses intersections and projected locations to determine if the tracker overlaps others.
		This means objects that overlap when first detected will not _both_ be added to the MultiTracker.
		"""

		for aTracker in self.trackers:
			if self._useVelocity:
				if self.intersects(aTracker, bbox) and self.projectedLocationMatches(aTracker, bbox):
					return True
			elif self.intersects(aTracker, bbox): return True
		return False

	def length(self):
		""" Get number of Trackers in the MultiTracker. """
		return len(self.trackers)

	def getFocus(self):
		""" Get focal object based on primaryTarget configuration.
		Currently only closest is supported - checks whether there is a tracker
		that is larger than the previous closest tracker by the configured threshold.
		"""

		if self._primaryTarget == "closest":
			focusChanged = False
			if self.focus:
				# area = self.focus.area()
				area = self.focus.area()
			else:
				area = None
			for aTracker in self.trackers:
				# If there's no focus or aTracker is larger than focus, and they aren't the same tracker
				if not self.focus or (aTracker.area() > area*(1+(self._closestThreshold/100)) 
					and self.focus.getCreated() != aTracker.getCreated()):
					focusChanged = True
					self.focus = aTracker
					area = aTracker.area()
			if focusChanged:
				return self.focus
			else:
				return None

		elif self._primaryTarget == "closest_engaged":
			#TODO
			self.logger.error('Primary Target %s is not implemented.'%self._primaryTarget)
			return None
		else:
			self.logger.error('Primary Target %s is not implemented.'%self._primaryTarget)
			return None

	def checkFocus(self):
		""" Check if focal Tracker has changed by updating the focus. """
		
		focus = self.getFocus()
		if focus:
			return True, focus.bbox
		else:
			return False, None
