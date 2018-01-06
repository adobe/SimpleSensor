"use strict";
class MotionDetectionMain {
    constructor(contextHub, eventElement, loggly) {

        this.SHOW_DISPLAY = true;
        this.SHOW_DIFF = true;
        this.SHOW_API_HIT_COUNT = true;

        //Default params for user presence
        this.MIN_CONFIDENCE = 0.8;
        this.GENDER_DIFF = 0.2;
        this.AGE_SMOOTH_VALUE = 10;

        //Face API 1.0 (Azure) settings
        this.FACE_LOCATION = "westus";
        this.FACE_URL = "https://" + this.FACE_LOCATION + ".api.cognitive.microsoft.com/face/v1.0/detect?";
        this.FACE_KEY = "1cb7baa5aeda40c586267e8d40bc19f9";
        this.FACE_CONTENT_TYPE = "application/octet-stream";

        this.CONTENT_TYPE = "application/octet-stream";

        this.loggly = loggly;
        this.contextHub = contextHub;
        this.eventElement = eventElement;

        //Default api parameters (PROJECT OXFORD/AZURE)
        this.API_PARAMS = {
            "returnFaceId": "true",
            "returnFaceLandmarks": "false",
            "returnFaceAttributes": "age,gender,glasses,facialHair"
        };

        this.defaultParams = {
            age: "unknown",
            gender: "unknown",
            glasses: "unknown",
            facialHair: "unknown"
        };

        this._cameraDeviceIndex = 1;

        //Video elements
        this.video = document.getElementById('video');
        this.videoCanvas = document.getElementById('videoCanvas');
        this.trackingJSCanvas = document.getElementById('canvas');
        this.context = this.trackingJSCanvas.getContext('2d');

        //diff elements
        this.diffCanvas = document.getElementById('diffCanvas');
        this.diffContext = this.diffCanvas.getContext('2d');
        this.diffContext.globalCompositeOperation = 'difference';
        this.diffCanvas.width = this.video.width;
        this.diffCanvas.height = this.video.height;

        // this.video.addEventListener("loadedmetadata", (e) => {
        //     this.diffCanvas.width = this.videoWidth;
        //     this.diffCanvas.height = this.videoHeight;
        // }, false);

        //placeholder websocket instance
        this.websocket = null;

        this.diffLoopOn = true;


        if (this.SHOW_DISPLAY === true) {
            $('#canvas, #video').fadeTo(0, 1);
        }

        if (this.SHOW_DIFF === true) {
            $('#diffCanvas').fadeTo(0, 1);
        }

        if(this.SHOW_API_HIT_COUNT === true){
            $('#apiHitCount').fadeTo(0,1);
        }
    }

    attachCameraStreamToWindow(options) {
        var that = this;
        return new Promise(function (resolve, reject) {
            var targetWindow = window;
            /* check options and set defaults if needed*/
            if (typeof options === "undefined") {
                options = {};
            }
            if (typeof options.cameraDeviceIndex === "undefined") {
                options.cameraDeviceIndex = that._cameraDeviceIndex;
            }
            if (typeof options.maxWidth === "undefined") {
                options.maxWidth = 2560
            }
            if (typeof options.minWidth === "undefined") {
                options.minWidth = 2560
            }

            var memomiCameraDevice;
            var videoDeviceCount = 1;
            navigator.mediaDevices.enumerateDevices()
                .then(function (devices) {
                    var videoSourceId;
                    console.log("found devices", devices);
                    devices.forEach(function (device) {
                        if (typeof device.label != "undefined") {
                            if (device.kind == "videoinput") {
                                if (videoDeviceCount == options.cameraDeviceIndex) {
                                    console.log("using camera ", device);
                                    memomiCameraDevice = device;
                                    videoSourceId = device.deviceId;
                                }
                                videoDeviceCount++;
                                return true;
                            }
                        } else {
                            console.warn("device.label was undefined", device);
                        }
                    });

                    start(memomiCameraDevice, options);
                })
                .catch(function (err) {
                    console.log(err.name + ": " + err.message);
                });

            //noinspection JSAnnotator
            function handleSuccess(stream) {
                console.debug('Stream success');
                targetWindow.cameraStream = stream; // make variable available to browser iframe window
                resolve(true);
            };

            //noinspection JSAnnotator
            function handleError(error) {
                console.log('navigator.mediaDevices.getUserMedia error: ', error);
                reject();
            };

            //noinspection JSAnnotator
            function start(videoDevice, options) {
                console.debug("starting stream for device ", videoDevice);

                //TODO: may need to pass in the constraints to the event
                var constraints = {
                    audio: false,
                    video: {
                        mandatory: {
                            sourceId: videoDevice.deviceId,
                            maxWidth: options.maxWidth,
                            minWidth: options.minWidth
                        }
                    }
                };

                navigator.mediaDevices.getUserMedia(constraints).then(handleSuccess).catch(handleError);
            };
        })
    }

    showScreensaver() {
        //Update the advertisement in target based on the face attributes

        //Animate the mbox into view and then reset detection
        $('.mboxDefault').animate({
            opacity: 0
        }, 750, function () {

            mboxUpdate('dms-2017-mbox', '/mode=screensaver', '/glasses=unknown', '/gender=unknown', '/facialHair=unknown', '/age=unknown');

        });

    }

    toggleShowVideo(){
        if (this.SHOW_DISPLAY === true) {
            //toggle show dislay
            this.SHOW_DISPLAY = false;
            $('#canvas, #video').fadeTo(1, 0);
        }
        else{
            //toggle show dislay
            this.SHOW_DISPLAY = true;
            $('#canvas, #video').fadeTo(0, 1);
        }
    }

    toggleShowApiCount(){
        if (this.SHOW_API_HIT_COUNT === true) {
            //toggle show api hit count
            this.SHOW_API_HIT_COUNT = false;
            $('#apihitcount').fadeTo(1, 0);
        }
        else{
            //toggle show api hit count
            this.SHOW_API_HIT_COUNT = true;
            $('#apiHitCount').fadeTo(0, 1);
        }
    }

    toggleShowDiff(){
        if (this.SHOW_DIFF === true) {
            this.SHOW_DIFF = false;
            $('#diffCanvas').fadeTo(1, 0);
        }
        else{
            //toggle show dislay
            this.SHOW_DIFF = true;
            $('#diffCanvas').fadeTo(0, 1);
        }
    }

    init(eventElement, contextHub) {

        this.eventElement = eventElement;
        this.contextHub = contextHub;

        //set external params
        this.setExternalParams();

        //Listen for events to update the interface
        this.addInterfaceEventListeners(this.eventElement);

        //Listen for events regarding to target mbox
        this.addTargetEventListeners(this.eventElement);

        //Set up listeners on buttons combos
        this.setupButtonEventListeners(this.eventElement);

        //Initialize the user presence, api, image buffer, image tracker classes, tracking js (ORDER IMPORTANT)
        this.up = new UserPresence(this.contextHub, this.MIN_CONFIDENCE, this.GENDER_DIFF);
        this.up.updateUserPresenceStore(this.defaultParams);
        this.api = new API(this.eventElement, 1); //second param is API flag, 0 = Adobe, 1 = Azure
        // this.api.buildAdobeAPI(this.URL);
        //this.api.buildAzureAPI(this.API_PARAMS, this.AGE_URL, this.CONTENT_TYPE, this.KEY);
        this.api.buildAzureAPI(this.API_PARAMS, this.FACE_URL, this.FACE_CONTENT_TYPE, this.FACE_KEY);
        this.imgTracker = new ImageTracker(this.videoCanvas, this.video, this.eventElement);

        //Listen for events from the classes
        this.addClassEventListeners();

        //start tracking with clmtrackr
        // this.initClmtrackr();
        // this.startDiffLoop();

        //setup websocket
        console.log('before new websocket');
        this.websocket = new WebsocketClient("127.0.0.1", 13254, eventElement);
        this.addWebsocketEventListeners();

        this.showScreensaver(); // Starts tracking on render

    }

    //FUNCTIONS

    //Set clmtrackr parameters
    setExternalParams() {
        var infoOverlay = document.getElementById("infoOverlay");
        this.faceThreshold = infoOverlay.getAttribute("data-face-threshold");
        this.convergenceThreshold = infoOverlay.getAttribute("data-convergence-threshold");
        this.DIFF_DELAY_LOOP = infoOverlay.getAttribute("diff-delay-loop");
        this.DIFF_PIXEL_THRESHOLD = infoOverlay.getAttribute("diff-pixel-threshold");
        this.DIFF_SCORE_THRESHOLD = infoOverlay.getAttribute("diff-score-threshold");
        this.MOTION_CAPTURE_DELAY = infoOverlay.getAttribute("motion-capture-delay");
        this.MOTION_CAPTURE_DELAY_NO_FACE = infoOverlay.getAttribute("motion-capture-delay-no-face");
        this.CLEAR_AD_DELAY = infoOverlay.getAttribute("clear-ad-delay");
        this.diffLoopCounter = 0;

        //override external parameters for testing
        this.faceThreshold = 0.50;
        this.convergenceThreshold = 2;
        this.DIFF_DELAY_LOOP = 100; //delay in milliseconds
        this.DIFF_PIXEL_THRESHOLD = 100;
        this.DIFF_SCORE_THRESHOLD = 80;
        this.MOTION_CAPTURE_DELAY = 1000; //delay in milliseconds
        this.MOTION_CAPTURE_DELAY_NO_FACE = 2000; //delay in milliseconds
    }

    //Start the tracking js (draws rectangles on canvas when a face is tracked)
    initTrackingJS() {
        // console.log('initializing tracking.js: ', this.tracker.getClassifiers());
        //
        // //Initialize the tracking functionality
        // this.tracker.setInitialScale(4);
        //
        // this.tracker.setStepSize(2);
        //
        // this.tracker.setEdgesDensity(0.1);
        //
        // this.trackerTask = tracking.track('#video', this.tracker, {camera: true});
        //
        // this.trackerTask.stop();
    }

    initClmtrackr() {

        //initialize clmtrackr object
        this.ctrackr = new clm.tracker({scoreThreshold: this.faceThreshold});
        this.start = null;
        this.ctrackrConverged = false;
        this.ctrackr.init();
        this.startClmtrackr();
    }

    stopTrackingJS() {
        // this.trackerTask.stop();
    }

    stopClmtrackr() {
        this.ctrackr.stop();
    }

    startTrackingJS() {

        var _this = this;

        // this.trackerTask.run();
        //
        // this.tracker.once('track', function(event) {
        //
        //     console.debug("Image Class: getting tracked image");
        //
        //     //Track face on canvas
        //     _this.context.clearRect(0, 0, _this.trackingJSCanvas.width, _this.trackingJSCanvas.height);
        //     event.data.forEach(function(rect) {
        //         _this.context.strokeStyle = '#a64ceb';
        //         _this.context.strokeRect(rect.x, rect.y, rect.width, rect.height);
        //         _this.context.font = '11px Helvetica';
        //         _this.context.fillStyle = "#fff";
        //         _this.context.fillText('x: ' + rect.x + 'px', rect.x + rect.width + 5, rect.y + 11);
        //         _this.context.fillText('y: ' + rect.y + 'px', rect.x + rect.width + 5, rect.y + 22);
        //     });
        //
        //     //Event thrown when face detected (listening in image tracker class)
        //     _this.throwTrackingJSEvent('face-tracked', "");
        // });
    }

    startDiffLoop() {
        this.diffLoopVariable = setInterval(this.diffLoop.bind(this), this.DIFF_DELAY_LOOP);
        this.diffLoopOn = true;
        this.diffLoopCounting = true;
        this.diffLoopCounter = 0; //reset loop counter
    }

    stopDiffLoop() {
        var that = this;
        this.diffLoopCounter = 0; //reset loop counter
        this.diffLoopCounting = false;
        return new Promise(function(resolve,reject){
            if(that.diffLoopVariable) clearInterval(that.diffLoopVariable);
            that.diffLoopOn = false;
            resolve();
        })
    }

    diffLoop() {
        var that = this;

        if(this.diffLoopCounting) {
            this.diffLoopCounter += 1; //increment loop counter
        }
        //if diff loop has run for a while without seeing anyone, update presence to unknown to reset to screensaver
        if(this.diffLoopCounter > this.CLEAR_AD_DELAY && this.diffLoopCounting) { //40 = 4s
            console.log('in loop counter > ', this.CLEAR_AD_DELAY, " : ", this.diffLoopCounter);
            this.diffLoopCounting = false;
            $('.mboxDefault').animate({
                opacity: 0
            }, 750, function () {
                //Update the advertisement in target based on the face attributes
                mboxUpdate('dms-2017-mbox', '/mode=screensaver', '/glasses=unknown' , '/gender=unknown', '/facialHair=unknown', '/age=unknown');

            });
            this.up.updateUserPresenceStore({gender: "Unknown", age: "Unknown", facialHair: "Unknown", glasses: "Unknown"});
            this.throwInterfaceEvent('smartad-update', {Gender: "Unknown", Age: "Unknown", Beard: "Unknown", Glasses: "Unknown"});
        }

        // console.log('diffcanvas: ', this.diffCanvas);
        this.diffContext.globalCompositeOperation = 'difference';
        this.diffContext.drawImage(this.video, 0, 0, this.diffCanvas.width, this.diffCanvas.height);

        //get imageData
        var imageData = this.diffContext.getImageData(0, 0, this.diffCanvas.width, this.diffCanvas.height);

        //get score
        var [diffScore, imageDataPost] = this.getDiffScore(imageData);

        //if score > threshold, there was motion detected
        if(diffScore > this.DIFF_SCORE_THRESHOLD){
            console.log('[trace] motion detected');
            console.log('diff score (', diffScore ,') > threshold (', this.DIFF_SCORE_THRESHOLD, ')');
            this.stopDiffLoop().then(() => {
                console.log('[trace] stopped diff loop');
                //if there is a face detected
                if(this.ctrackr.getScore() > this.faceThreshold) {
                    console.log('[trace] face detected');
                    //if clmtrackr has converged
                    if(this.ctrackr.getConvergence() < this.convergenceThreshold){
                        console.log('[trace] tracker converged');
                        //start diff loop after timeout
                        setTimeout(function(){
                            that.startDiffLoop();
                        }, that.MOTION_CAPTURE_DELAY);
                    } else { //tracker hasn't converged
                        console.log('[trace] tracker not converged');

                        //sample video and start diff loop after delay
                        setTimeout(function(){
                            that.sampleVideoStartDiffLoop();
                        }, that.MOTION_CAPTURE_DELAY);
                    }

                } else { //no face detected, start diff loop after timeout
                    console.log('[trace] no face detected');

                    setTimeout(function(){
                        that.sampleVideoStartDiffLoop();
                    }, that.MOTION_CAPTURE_DELAY_NO_FACE);
                }
            })
        }

        //ready diff context
        this.diffContext.globalCompositeOperation = 'source-over';
        this.diffContext.drawImage(video, 0, 0, this.diffCanvas.width, this.diffCanvas.height);
    }

    getDiffScore(imageData) {

        //get diff score
        var diffScore = 0;
        var imageDataPost = imageData;
        // console.log('imagedata: ', imageData);
        for (var i = 0; i < imageData.data.length; i += 4) {
            var r = imageData.data[i] / 3;
            var g = imageData.data[i + 1] / 3;
            var b = imageData.data[i + 2] / 3;
            var pixelScore = r + g + b;

            //set imagedatapost
            imageDataPost.data[i] = 0;
            imageDataPost.data[i + 1] *= 2;
            imageDataPost.data[i+2] = 0;

            if (pixelScore >= this.DIFF_PIXEL_THRESHOLD) {
                // console.log('pixel score (', pixelScore, ') >= threshold (', this.DIFF_PIXEL_THRESHOLD, ')');

                diffScore++;
            }
        }
        console.log('diff score: ', diffScore);
        return [diffScore, imageDataPost];
    }

    sampleVideoStartDiffLoop(){
        this.throwClmtrackrEvent('face-tracked', "");
        this.startDiffLoop();
    }

    stopDiffSampleVideo() {
        var that = this;

        //stop diff loop
        this.stopDiffLoop();

        return new Promise(function(resolve, reject){
            //wait then sample image
            setTimeout(function(){

                //sample video and send to azure
                that.throwClmtrackrEvent('face-tracked', "");
                resolve();

            }, that.MOTION_CAPTURE_DELAY);
        });

    }

    clmTrackrDrawLoop(timestamp) {

        //get progress -> use for cutting down on API call frequency
        if (!this.start) this.start = timestamp;
        var progress = timestamp - this.start;

        // console.log('score: ', this.ctrackr.getScore(), " || convergence: ", this.ctrackr.getConvergence());
        //recurse animation frame, keep current scope
        requestAnimationFrame(this.clmTrackrDrawLoop.bind(this));
        var cc = this.trackingJSCanvas.getContext('2d');
        //clear face trace
        cc.clearRect(0, 0, this.trackingJSCanvas.width, this.trackingJSCanvas.height);

        //if score is above threshold -> draw face trace & take frame to compare to previous
        if (this.ctrackr.getScore() > this.faceThreshold) {

            //if the canvas is visible and exists, draw face
            if(this.SHOW_DISPLAY && this.trackingJSCanvas) this.ctrackr.draw(this.trackingJSCanvas);

            //get convergence -> if the image has converged, emit event and set flag
            if (this.ctrackr.getConvergence() < this.convergenceThreshold) {
                //emit event if converged flag is false (first time sensing convergence)
                if (!this.ctrackrConverged) {
                    // console.log('throwing face-tracked event');
                    // this.throwClmtrackrEvent('face-tracked', "");
                }

                //set flag
                this.ctrackrConverged = true;
            }
            else { //no convergence -> set flag to false
                this.ctrackrConverged = false;
            }
        }

    }

    startClmtrackr() {
        //start clm on video feed
        // this.ctrackr.start(this.video);

        //pass up scope to the animation
        // requestAnimationFrame(this.clmTrackrDrawLoop.bind(this));
    }

    //Get the current date (used for loggly posts)
    getCurrentDate() {
        var currentdate = new Date();

        //Build the date
        var datetime = currentdate.getDate() + "/"
            + (currentdate.getMonth() + 1) + "/"
            + currentdate.getFullYear() + " @ "
            + currentdate.getHours() + ":"
            + currentdate.getMinutes() + ":"
            + currentdate.getSeconds();

        return datetime;
    }

    //Throw tracking js events, used to get image to send to API
    throwTrackingJSEvent(eventName, attributes) {

        this.stopTrackingJS();

        var customEventName = "trackingjs-" + eventName;

        console.debug("dispatching trackingjs event " + customEventName);

        var aEvent = new CustomEvent(customEventName, {'detail': attributes});

        this.eventElement.dispatchEvent(aEvent);
    }

    //Throw Clmtrackr event
    throwClmtrackrEvent(eventName, attributes) {

        // this.stopClmtrackr();

        var customEventName = "clmtrackr-" + eventName;

        console.debug("dispatching clmtrackr event " + customEventName);

        var aEvent = new CustomEvent(customEventName, {'detail': attributes});

        this.eventElement.dispatchEvent(aEvent);
    }

    //Throw interface events, used to update interface
    throwInterfaceEvent(eventName, attributes) {

        var customEventName = "interface-" + eventName;

        // console.debug("dispatching interface event " + customEventName);

        var aEvent = new CustomEvent(customEventName, {'detail': attributes});

        this.eventElement.dispatchEvent(aEvent);
    }

    //Check if there were faces in the API data returned
    updateSettings(faceData) {
        if (faceData !== undefined) {

            //Save those values to an object to send with interface event
            var interfaceParams = {
                'Age': "unknown",
                'Glasses': "unknown",
                'Beard': "unknown",
                'Gender': "unknown"
            };

            //Show the face attributes
            console.debug("Male confidence is: " + faceData.maleConfidence);
            console.debug("Female confidence is: " + faceData.femaleConfidence);
            console.debug("Glasses confidence is: " + faceData.glassesConfidence);
            console.debug("Beard confidence is: " + faceData.beardConfidence);
            console.debug("Age is: " + faceData.age);

            var ageNaN = isNaN(parseFloat(faceData.age));
            var oldAge = this.up.getParam("age");

            //Set the face attributes in the presence store and return if there was a change to the data
            var genderVal = this.up.setGender(faceData.femaleConfidence, faceData.maleConfidence);
            var glassesVal = this.up.setGlasses(faceData.glassesConfidence);
            var facialHairVal = this.up.setFacialHair(faceData.beardConfidence);
            var ageVal = this.up.setAge(faceData.age, this.AGE_SMOOTH_VALUE);

            if ((faceData.age == "unknown" || ageNaN == true) && oldAge != "unknown") {
                this.showScreensaver();

                //Update interface
                this.throwInterfaceEvent('smartad-update', interfaceParams);
            } else if (faceData.age == "unknown" && oldAge == "unknown") {
                // this.startTrackingJS();

                //Update interface
                this.throwInterfaceEvent('smartad-update', interfaceParams);
            } else {

                if (genderVal != false || ageVal != false || facialHairVal != false || glassesVal != false) {

                    //Get the updated values from the presence store
                    ageVal = this.up.getParam("age");
                    glassesVal = this.up.getParam("glasses");
                    facialHairVal = this.up.getParam("facialHair");
                    genderVal = this.up.getParam("gender");

                    //Save those values to an object to send with interface event
                    var interfaceParams = {
                        'Age': ageVal,
                        'Glasses': glassesVal,
                        'Beard': facialHairVal,
                        'Gender': genderVal
                    };

                    //Update interface
                    this.throwInterfaceEvent('smartad-update', interfaceParams);

                    //Animate the mbox into view and then reset detection
                    $('.mboxDefault').animate({
                        opacity: 0
                    }, 750, function () {
                        //Update the advertisement in target based on the face attributes
                        mboxUpdate('dms-2017-mbox', '/mode=ads', '/glasses=' + glassesVal, '/gender=' + genderVal, '/facialHair=' + facialHairVal, '/age=' + ageVal);

                    });
                } else {
                    // this.startTrackingJS();
                    // this.startClmtrackr();
                }
            }
        } else {
            // this.startTrackingJS();
            // this.startClmtrackr();
        }
    }

    logData(params) {
        this.loggly.push(params);
    }

    addWebsocketEventListeners(){
        console.log('adding websocket events');
        this.websocket.on("message", function(eventData){
            console.log("event data: ", eventData);
        });
    }

    addTargetEventListeners(eventElement) {

        var _this = this;
        //Request to update mbox failed
        this.eventElement.addEventListener(adobe.target.event.REQUEST_FAILED, function (event) {
            console.log('Event', event);
        });

        //Request to update mbox succeeded
        this.eventElement.addEventListener(adobe.target.event.REQUEST_SUCCEEDED, function (event) {
            console.log('Event', event);

            // _this.startTrackingJS();
            _this.startClmtrackr();
        });

        //Request to render content succeeded
        this.eventElement.addEventListener(adobe.target.event.CONTENT_RENDERING_SUCCEEDED, function (event) {
            console.log('Event', event);

            //Animate the mbox into view and then reset detection
            $('.mboxDefault').animate({
                opacity: 1
            }, 750, function () {

                // _this.startTrackingJS();
                _this.startClmtrackr();
            });
        });

        //Request to render content failed
        this.eventElement.addEventListener(adobe.target.event.CONTENT_RENDERING_FAILED, function (event) {
            console.log('Event', event);

            // _this.startTrackingJS();
            _this.startClmtrackr();
        });

    }

    addInterfaceEventListeners(eventElement) {

        var _this = this;

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('interface-smartad-update', function (e) {
            var attributes = e.detail;

            var genderElem = $('#contextHubGender');
            var ageElem = $('#contextHubAge');
            var tagsElem = $('#contextHubTags');
            var glassesElem = $('#contextHubGlasses');
            var beardElem = $('#contextHubBeard');

            genderElem.html(attributes.Gender);
            ageElem.html(attributes.Age);
            tagsElem.html(attributes.Gender + ',  ' + attributes.Age + ',  ' + attributes.Beard + ',  ' + attributes.Glasses);
            glassesElem.html(attributes.Glasses);
            beardElem.html(attributes.Beard);

        }, false);
    }

    addClassEventListeners() {
        var _this = this;

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('image-tracker-get-tracked-image-success', function (e) {

            console.debug("API Class: receiving image blob");

            var blob = e.detail;

            _this.api.pushAPIRequest(blob);


        });

        this.eventElement.addEventListener('trackingjs-face-tracked', function (e) {

            console.debug("Image Tracker Class: getting tracked image <tracking.js>");

            _this.imgTracker.getTrackedImageBlob();

        });

        this.eventElement.addEventListener('clmtrackr-face-tracked', function (e) {

            console.debug("Image Tracker Class: getting tracked image <clmtrackr>");

            _this.imgTracker.getTrackedImageBlob();

        });

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('api-all-data-received-success', function (e) {

            console.debug("Main Class: updating settings");

            var faceData = e.detail;

            _this.updateSettings(faceData);
        });

        //Listen for Azure success events
        this.eventElement.addEventListener('api-azure-data-received-success', function (e) {

            console.debug("Main class: successfully received Azure data; updating");

            var faceData = e.detail;

            _this.updateSettings(faceData);
        });

        //Listen for Adobe success events
        this.eventElement.addEventListener('api-adobe-data-received-success', function (e) {

            console.debug("Main class: successfully received Adobe data; updating");

            var faceData = e.detail;

            _this.updateSettings(faceData);
        });


        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('api-azure-data-received-failure', function (e) {

            console.debug("API Class: data received failure");

            // _this.startTrackingJS();
            _this.startClmtrackr();
        });

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('api-adobe-data-received-failure', function (e) {

            console.debug("API Class: data received failure");

            // _this.startTrackingJS();
            _this.startClmtrackr();
        });

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('image-tracker-get-tracked-image-failure', function (e) {

            console.debug("Image Tracker Class: image tracker failure");

            // _this.startTrackingJS();
            _this.startClmtrackr();


        });
    }

    setupButtonEventListeners(){
        var that = this;

        this.eventElement.addEventListener("keydown", function(e){

            //ctrl + a pressed
            if (e.keyCode === 65 && e.ctrlKey){
                //toggle show/hide diff
                that.toggleShowDiff();
            }
            //ctrl + s pressed
            else if(e.keyCode === 83 && e.ctrlKey){
                //toggle show/hide video feed
                that.toggleShowVideo();
            }
            //ctrl + d pressed
            else if(e.keyCode === 68 && e.ctrlKey){
                //toggle show/hide api hit count
                that.toggleShowApiCount();
            }
        });
    }

}