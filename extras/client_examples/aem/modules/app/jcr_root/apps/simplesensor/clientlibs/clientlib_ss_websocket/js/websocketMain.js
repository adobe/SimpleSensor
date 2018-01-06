"use strict";
class WebsocketMain{
    constructor(){
        this.SHOW_API_HIT_COUNT = false;
        this.SHOW_DISPLAY = false;

        //Default params for user presence
        this.MIN_CONFIDENCE = 0.6;
        this.GENDER_DIFF = 0.2;
        this.AGE_SMOOTH_VALUE = 10;

        //Face API 1.0 (Azure) settings
        this.FACE_LOCATION = "westus";
        this.FACE_URL = "https://" + this.FACE_LOCATION + ".api.cognitive.microsoft.com/face/v1.0/detect?";
        this.FACE_KEY = "1cb7baa5aeda40c586267e8d40bc19f9";
        this.FACE_CONTENT_TYPE = "application/octet-stream";

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

        this.websocket = null;
        this.up = null;
        this.interval = null;

        if(this.SHOW_API_HIT_COUNT === true){
            $('#apiHitCount').fadeTo(0,1);
        }

        if (this.SHOW_DISPLAY === true) {
            $('#canvas, #video').fadeTo(0, 1);
        }
    }

    //dummy function to work like motiondetection
    attachCameraStreamToWindow(){
        return new Promise(function(resolve, reject){
            resolve();
        });
    }

    reconnectSocket(){
        //try to reconnect
        if(!this.ignoreClose) {
            console.debug('Websocket failed to connect, retrying in ', Math.min(this.reconnectInterval * 1000 * this.reconnectCount+1, this.reconnectMax * 1000), " ms");
            this.ignoreClose = true;
            this.websocket.reconnect();
            this.reconnectTimer = setTimeout(this.reconnectSocketLoop.bind(this), Math.min(this.reconnectInterval * 1000 * ++this.reconnectCount, this.reconnectMax * 1000));
        }
    }

    reconnectSocketLoop(){
        this.websocket.reconnect();
        console.debug('Websocket failed to connect, retrying in ', Math.min(this.reconnectInterval * 1000 * this.reconnectCount+1, this.reconnectMax * 1000), " ms");
        this.reconnectTimer = setTimeout(this.reconnectSocketLoop.bind(this), Math.min(this.reconnectInterval * 1000 * ++this.reconnectCount, this.reconnectMax * 1000));
    }

    socketConnected(){
        console.debug('Websocket reconnected');
        if(this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        this.reconnectTimer = null;
        this.ignoreClose = false;
        this.reconnectCount = 0;
    }

    showScreensaver() {
        //Show a random couple ad
        $('.mboxDefault').animate({
            opacity: 0
        }, 750, function () {
            //pick random age from 18 to 60, show couples ad for that age group
            let ranAge = Math.floor(Math.random()*(60-18+1)+18);
            console.log('random age: ', ranAge);
            mboxUpdate('dms-2017-mbox', '/mode=ads', '/glasses=unknown', '/gender=unknown', '/facialHair=unknown', '/age='+ranAge);
        });

        //Start timer to keep showing random couple ads
        this.interval = setInterval(function(){
            //Animate the mbox into view and then reset detection
            $('.mboxDefault').animate({
                opacity: 0
            }, 750, function () {
                //pick random age from 18 to 60, show couples ad for that age group
                let ranAge = Math.floor(Math.random()*(60-18+1)+18);
                console.log('random age: ', ranAge);
                mboxUpdate('dms-2017-mbox', '/mode=ads', '/glasses=unknown', '/gender=unknown', '/facialHair=unknown', '/age='+ranAge);

                // screensaver version below
                // mboxUpdate('dms-2017-mbox', '/mode=screensaver', '/glasses=unknown', '/gender=unknown', '/facialHair=unknown', '/age=unknown');
            });
        }, this.adTimer*1000);

    }

    getFocalFaceData(eventData){
        var faceData = {};
        console.log('eventData: ', eventData);
        let predictions = eventData._extendedData.predictions;
        if(predictions.length > 0) {
            faceData.maleConfidence = predictions[0].faceAttributes.gender === "male" ? 1 : 0;
            faceData.femaleConfidence = 1 - this.maleConfidence;
            faceData.age = predictions[0].faceAttributes.age || this.age || "unknown";
            faceData.beardConfidence = predictions[0].faceAttributes.facialHair.beard;
            faceData.glassesConfidence = predictions[0].faceAttributes.glasses === "ReadingGlasses" ? 1 : 0;
        }
        return faceData;
    }

    setExternalParams(){
        var infoOverlay = document.getElementById("infoOverlay");
        this.adTimer = infoOverlay.getAttribute("ad-timer"); // ad timer in seconds
        this.reconnectInterval = infoOverlay.getAttribute("websocket-reconnect-interval"); //starting reconnect interval in seconds
        this.reconnectMax = infoOverlay.getAttribute("websocket-reconnect-max"); //maximum reconnect interval in seconds
        this.contextHubVisibleTimer = infoOverlay.getAttribute("context-hub-visible-timer"); //time idle before hiding contexthub
    }

    // Forward websocket events to main event element
    throwWebsocketEvent(name, data){
        var fullName = "websocket-" + name;
        var event = new CustomEvent(fullName, {'detail': data});
        this.eventElement.dispatchEvent(event);
    }

    addWebsocketEventListeners(){
        console.log('adding websocket events');
        var self = this;

        // Listen for websocket messages
        this.websocket.on("message", function(eventData){
            if(eventData._topic === "Reset mBox"){ //if message is to reset
                if(!self.up.isUnknown()) { //and the mbox requires a reset
                    console.log('Reset mbox');
                    self.throwWebsocketEvent('reset-mbox', eventData);
                }
            }
            else if (eventData._topic === "Found face"){ //or throw found event
                if (eventData._extendedData.predictions.length > 0) { //if there is at least one prediction
                    self.throwWebsocketEvent('face-data-received', eventData);
                }
            }
            else if(eventData._topic === "blob") { //or throw blob event
                self.throwWebsocketEvent('incoming-blob', eventData);
            }
            else if (eventData.type === "close"){ //close message
                if(!self.ignoreClose) {
                    self.reconnectSocket();
                }
            }
            else if(eventData.type === "open"){ //open message
                self.socketConnected();
            }

        });

        // if websocket was successfully opened, stop timer
        // this.websocket.on("open", function(eventData){
        //     console.log('in main class open: ', eventData);
        //     self.socketConnected();
        // });
        //
        // // if websocket was closed, set growing timer to reconnect
        // this.websocket.on("close", function(eventData){
        //    console.log('in main class close: ', eventData);
        //     self.reconnectSocket();
        // });
    }

    addTargetEventListeners() {

        var _this = this;
        //Request to update mbox failed
        this.eventElement.addEventListener(adobe.target.event.REQUEST_FAILED, function (event) {
            console.log('Event', event);
        });

        //Request to update mbox succeeded
        this.eventElement.addEventListener(adobe.target.event.REQUEST_SUCCEEDED, function (event) {
            console.log('Event', event);

        });

        //Request to render content succeeded
        this.eventElement.addEventListener(adobe.target.event.CONTENT_RENDERING_SUCCEEDED, function (event) {
            console.log('Event', event);

            //Animate the mbox into view and then reset detection
            $('.mboxDefault').animate({
                opacity: 1
            }, 750, function () {

            });
        });

        //Request to render content failed
        this.eventElement.addEventListener(adobe.target.event.CONTENT_RENDERING_FAILED, function (event) {
            console.log('Event', event);

        });

    }

    addInterfaceEventListeners() {

        var self = this;

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('interface-smartad-update', function (e) {

            var attributes = e.detail;

            var genderElem = $('#contextHubGender');
            var ageElem = $('#contextHubAge');
            var tagsElem = $('#contextHubTags');
            var glassesElem = $('#contextHubGlasses');
            var beardElem = $('#contextHubBeard');

            genderElem.html(attributes.Gender + 'ish');
            ageElem.html(attributes.Age);
            if(attributes.Gender === "female"){
                tagsElem.html(attributes.Gender + ',  ' + attributes.Age + 'ish,  ' + attributes.Glasses);
            }
            else{
                tagsElem.html(attributes.Gender + ',  ' + attributes.Age + 'ish,  ' + attributes.Beard + ',  ' + attributes.Glasses);
            }
            glassesElem.html(attributes.Glasses);
            beardElem.html(attributes.Beard);

        }, false);
    }

    addClassEventListeners(){

        var self = this;
        //Listen for Azure success events
        this.eventElement.addEventListener('api-azure-data-received-success', function (e) {

            console.debug("Main class: successfully received Azure data; updating");

            var faceData = e.detail;

            self.updateSettings(faceData);
        });

        //direct to websocket success events
        this.eventElement.addEventListener('websocket-face-data-received', function (e) {

            console.debug("Main class: successfully received websocket data; updating");

            var faceData = self.getFocalFaceData(e.detail);

            self.updateSettings(faceData);
        });

        //Listen for Azure fails
        this.eventElement.addEventListener('api-azure-data-received-failure', function (e) {

            console.debug("API Class: data received failure");

        });

        //Listen for face mode and then populate overlay
        this.eventElement.addEventListener('websocket-face-detected', function (e) {

            console.debug("API Class: receiving image blob");

            var data = e.detail._extendedData.imageData;
            var dataType = e.detail._extendedData.dataType;
            var blob = self.b64toBlob(data, dataType, 512);
            self.api.pushAPIRequest(blob);

        });

        this.eventElement.addEventListener('websocket-incoming-blob', function(e){
            // console.log('displaying incoming blob');
            var data = e.detail._extendedData.imageData;
            var dataType = e.detail._extendedData.dataType;
            var blob = self.b64toBlob(data, dataType, 512);
            console.log('about to render blob');
            document.getElementById('canvas').renderImage(blob);
        });

        //Listen for reset m-box cues
        this.eventElement.addEventListener('websocket-reset-mbox', function (e) {

            console.debug("API Class: resetting mbox");

            self.resetMbox();

        });
    }

    b64toBlob(b64Data, contentType, sliceSize) {
        contentType = contentType || '';
        sliceSize = sliceSize || 512;

        var byteCharacters = atob(b64Data);
        var byteArrays = [];

        for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
            var slice = byteCharacters.slice(offset, offset + sliceSize);

            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }

            var byteArray = new Uint8Array(byteNumbers);

            byteArrays.push(byteArray);
        }

        var blob = new Blob(byteArrays, {type: contentType});
        return blob;
    }

    //Check if there were faces in the API data returned
    updateSettings(faceData) {
        const self = this;
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
                // this.showScreensaver();

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
                        console.log('Clearing interval');
                        //cancel the screensaver timer interval
                        clearInterval(self.interval);

                        //Update the advertisement in target based on the face attributes
                        mboxUpdate('dms-2017-mbox', '/mode=ads', '/glasses=' + glassesVal, '/gender=' + genderVal, '/facialHair=' + facialHairVal, '/age=' + ageVal);

                    });
                }
            }
        } else {

            // this.resetMbox();
        }
    }

    resetMbox(){
        console.log('in reset mbox');
        this.showScreensaver();
        this.throwInterfaceEvent('smartad-update', {
            Gender: "Unknown",
            Age: "Unknown",
            Beard: "Unknown",
            Glasses: "Unknown"
        });
        this.up.updateUserPresenceStore({
            gender: "Unknown",
            age: "Unknown",
            facialHair: "Unknown",
            glasses: "Unknown"
        });

        //start timer to hide contexthub
        clearTimeout(this.contextHubHideTimer);
        this.contextHubHideTimer = setTimeout(this.hideContextHubBar.bind(this), this.contextHubVisibleTimer*1000);
    }


    //Throw interface events, used to update interface
    throwInterfaceEvent(eventName, attributes) {

        var customEventName = "interface-" + eventName;

        var aEvent = new CustomEvent(customEventName, {'detail': attributes});

        this.eventElement.dispatchEvent(aEvent);
    }

    hideContextHubBar(){
        console.log('hiding bar');
        this.contextHubVisible = !this.contextHubVisible;
        $(".contexthub-container").animate({"top":"-4.175rem"}, 1000);
    }

    showContextHubBar(){
        this.contextHubVisible = !this.contextHubVisible;
        $(".contexthub-container").animate({"top":"0rem"}, 1000);

        //start timer to hide contexthub
        clearTimeout(this.contextHubHideTimer);
        this.contextHubHideTimer = setTimeout(this.hideContextHubBar.bind(this), this.contextHubVisibleTimer*1000);
    }

    hideInfo(){
        this.infoVisible = !this.infoVisible;
        $("#infoContainer").animate({"opacity":"0"}, 1000);
    }

    showInfo(){
        this.infoVisible = !this.infoVisible;
        $("#infoContainer").animate({"opacity":"1"}, 1000);
    }
    
    addInterfaceInteractions(){
        var self = this;
        document.getElementById("contextHubHideArea").addEventListener("click", function(){
            console.log('hiding bar');
            if(self.contextHubVisible){ //animate hiding contexthub
                console.log('hiding context hub bar');
                self.hideContextHubBar();
            }
            else{ //animate revealing contexthub
                self.showContextHubBar();
                console.log('showing context hub bar');
            }
        });

        document.getElementById("infoButtonContainer").addEventListener("click", function(){
            if(self.infoVisible){ //animate hiding info
                self.hideInfo();
                console.log('hiding info');
            }
            else{ //animate revealing info
                self.showInfo();
                console.log('showing info');
            }
        });

        document.getElementById('canvas').addEventListener("click", function(){
           if(self.SHOW_DISPLAY){
               self.SHOW_DISPLAY = !self.SHOW_DISPLAY;
               $('#canvas, #video').animate({'opacity':'0'}, 1000);
           }
           else{
               self.SHOW_DISPLAY = !self.SHOW_DISPLAY;
               $('#canvas, #video').animate({'opacity':'1'}, 1000);
           }
        });
    }

    addCanvasBlobRender(){
        HTMLCanvasElement.prototype.renderImage = function(blob){

            var ctx = this.getContext('2d');
            var img = new Image();

            img.onload = function(){
                ctx.drawImage(img, 0, 0)
            };

            img.src = window.URL.createObjectURL(blob);
        };
    }

    init(eventElement, contextHub) {

        this.eventElement = eventElement;
        this.contextHub = contextHub;

        //add HTML canvas render method
        this.addCanvasBlobRender();

        //set external params
        this.setExternalParams();

        this.addTargetEventListeners(eventElement);
        this.addInterfaceEventListeners(eventElement);
        this.addClassEventListeners(eventElement);

        //Initialize the user presence, api, image buffer, image tracker classes, tracking js (ORDER IMPORTANT)
        this.up = new UserPresence(this.contextHub, this.MIN_CONFIDENCE, this.GENDER_DIFF);
        this.up.updateUserPresenceStore(this.defaultParams);
        this.api = new API(this.eventElement, 1); //second param is API flag, 0 = Adobe, 1 = Azure
        this.api.buildAzureAPI(this.API_PARAMS, this.FACE_URL, this.FACE_CONTENT_TYPE, this.FACE_KEY);

        //setup websocket
        this.ignoreClose = false;
        this.reconnectTimer = null;
        this.reconnectCount = 0;
        this.websocket = new WebsocketClient("127.0.0.1", 13254);
        this.addWebsocketEventListeners();

        // setup contexthub bar hiding and info hot spot
        this.contextHubVisible = false;
        this.infoVisible = false;
        this.addInterfaceInteractions();

        if(!this.contextHubVisible){
            $(".contexthub-container").animate({"top":"-4.175rem"}, 1000);
        }

        this.showScreensaver(); // Starts tracking on render

    }

}