class ImageTracker{

    constructor(videoCanvas, video, eventElement){
        console.log('video width and height: ', video.videoWidth, video.videoHeight);
        this.eventElement = eventElement;
        this.videoCanvas = videoCanvas;
        this.video = video;
    }

    getTrackedImageBlob(){

        var _this = this;

        try {
            _this.videoCanvas.width = _this.video.videoWidth;
            _this.videoCanvas.height = _this.video.videoHeight;
            _this.videoCanvas.getContext('2d').drawImage(video, 0, 0, _this.videoCanvas.width, _this.videoCanvas.height);

            //Works in Chrome, check if not using that
            _this.videoCanvas.toBlob(function(blob){

                _this.throwImageEvent('get-tracked-image-success', blob);

            }, "image/jpeg", 1.0);

        } catch (e) {

            this.throwImageEvent('get-tracked-image-failure', e);

        }
    };

    //Throw interface events, used to update interface
    throwImageEvent(eventName, attributes){

        var customEventName = "image-tracker-"+eventName;

        console.debug("Image Tracker Class: dispatching event " + customEventName);

        var aEvent = new CustomEvent(customEventName, {'detail': attributes});

        this.eventElement.dispatchEvent(aEvent);
    }

}