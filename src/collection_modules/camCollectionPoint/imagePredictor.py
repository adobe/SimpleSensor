"""
ImagePredictor
Image predictor abstract class
"""
class ImagePredictor(object):
    """ Class that gives abstract definition of a prediction engine.
    Can be used to extend to your own local ML implementation or another API.
    """
    def getPrediction(self, image):
        raise NotImplementedError()
