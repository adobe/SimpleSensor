"""
Image prediction abstract class
author: DaViD bEnGe
date: 10/30/2017

"""
class AbstractImagePrediction(object):
    """ Class that gives abstract definition of a prediction engine.
    Can be used to extend to your own local ML implementation or another API.
    """
    def getPrediction(self, image):
        raise NotImplementedError()
