from threadsafeLogger import ThreadsafeLogger
from abstractImagePrediction import AbstractImagePrediction
import urllib.parse, base64, json, requests
import logging

class AzureImagePrediction(AbstractImagePrediction):
    def __init__(self, moduleConfig=None, loggingQueue=None):
        """ Initialize new AzureImagePrediction instance.
        Set parameters required by Azure Face API.
        """
        logging.basicConfig(level=logging.CRITICAL)
        self.logger = ThreadsafeLogger(loggingQueue, "AzureImagePrediction") # Setup logging queue
        self.config = moduleConfig

        # Constants
        self._subscriptionKey = self.config['Azure']['SubscriptionKey']
        self._uriBase = self.config['Azure']['UriBase']

        self._headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': self.config['Azure']['SubscriptionKey'],
        }
        self._params = urllib.parse.urlencode({
            "returnFaceId": "true",
            "returnFaceLandmarks": "false",
            "returnFaceAttributes": "age,gender,glasses,facialHair"
        })

    def getPrediction(self, imageBytes):
        """ Get prediction results from Azure Face API.
        Returns object with either a predictions array property or an error property.
        """

        resultData = {}

        try:
            tempResult = self.__getPrediction(imageBytes)
            resultData['predictions'] = tempResult

        except Exception as e:
            self.logger.error('Error getting prediction: %s'%e)
            resultData['error'] = str(e)

        return resultData

    def __getPrediction(self,imageBytes):
        """ Execute REST API call and return result """

        if len(self._subscriptionKey) < 10:
            raise EnvironmentError('Azure subscription key - %s - is not valid'%self._subscriptionKey)
        else:
            try:
                api_url = "https://%s/face/v1.0/detect?%s"% (self._uriBase, self._params)
                r = requests.post(api_url,
                    headers=self._headers,
                    data=imageBytes)

                if r.status_code != 200:
                    raise ValueError(
                        'Request to Azure returned an error %s, the response is:\n%s'
                        % (r.status_code, r.text)
                    )
                    
                jsonResult = r.json()
                self.logger.debug("Got azure data %s" %jsonResult)
                return jsonResult

            except Exception as e:
                self.logger.error(e)
