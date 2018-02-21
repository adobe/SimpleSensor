"use strict";
class WebsocketDemoMain{
    constructor(){
        this.SHOW_DISPLAY = false;

        // Default params for user presence
        this.MIN_CONFIDENCE = 0.6;
        this.GENDER_DIFF = 0.2;
        this.AGE_SMOOTH_VALUE = 10;

        this.defaultParams = {
            age: "unknown",
            gender: "unknown",
            glasses: "unknown",
            facialHair: "unknown"
        };

        this.websocket = null;
        this.up = null;
    }

    init(eventElement, contextHub) {

        this.eventElement = eventElement;
        this.contextHub = contextHub;

        // Add HTML canvas blob render method
        this.addCanvasBlobRender();

        // Initialize external params
        this.setExternalParams();

        // Add interface and class EventListeners
        this.addInterfaceEventListeners(eventElement);
        this.addClassEventListeners(eventElement);

        // Initialize UserPresence
        this.up = new SimpleSensorUserPresenceUpdateHelper(this.contextHub, this.MIN_CONFIDENCE, this.GENDER_DIFF);
        this.up.updateUserPresenceStore(this.defaultParams);

        // Initialize websocket
        this.ignoreClose = false;
        this.reconnectTimer = null;
        this.reconnectCount = 0;
        this.websocket = new WebsocketClient("127.0.0.1", 13254);
        this.addWebsocketEventListeners();

        // Set ContextHub bar and info overlay visibility
        this.contextHubVisible = false;
        this.infoVisible = false;

        // Add click events to interface elements
        this.addInterfaceInteractions();

        // Hide/show elements
        if(!this.contextHubVisible){
            $(".contexthub-container").animate({"top":"-4.175rem"}, 1000);
        }

        if(!this.infoVisible){
            $("#infoContainer").animate({"opacity":"0"}, 1000);
        }

        if (this.SHOW_DISPLAY === true) {
            $('#canvas, #video').fadeTo(0, 1);
        }
    }

    reconnectSocket(){
        //try to reconnect
        if(!this.ignoreClose) {
            console.debug('[WebsocketDemoMain] Websocket failed to connect, retrying in ', Math.min(this.reconnectInterval * 1000 * this.reconnectCount+1, this.reconnectMax * 1000), " ms");
            this.ignoreClose = true;
            this.websocket.reconnect();
            this.reconnectTimer = setTimeout(this.reconnectSocketLoop.bind(this), Math.min(this.reconnectInterval * 1000 * ++this.reconnectCount, this.reconnectMax * 1000));
        }
    }

    reconnectSocketLoop(){
        this.websocket.reconnect();
        console.debug('[WebsocketDemoMain] Websocket failed to connect, retrying in ', Math.min(this.reconnectInterval * 1000 * this.reconnectCount+1, this.reconnectMax * 1000), " ms");
        this.reconnectTimer = setTimeout(this.reconnectSocketLoop.bind(this), Math.min(this.reconnectInterval * 1000 * ++this.reconnectCount, this.reconnectMax * 1000));
    }

    socketConnected(){
        console.debug('[WebsocketDemoMain] Websocket reconnected');
        if(this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        this.reconnectTimer = null;
        this.ignoreClose = false;
        this.reconnectCount = 0;
    }

    getFocalFaceData(eventData){
        // Get demographic data from first face in response; clean and return it.
        var faceData = {};
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
        // Set constants from infoOverlay
        var infoOverlay = document.getElementById("infoOverlay");
        this.reconnectInterval = infoOverlay.getAttribute("websocket-reconnect-interval"); //starting reconnect interval in seconds
        this.reconnectMax = infoOverlay.getAttribute("websocket-reconnect-max"); //maximum reconnect interval in seconds
        this.contextHubVisibleTimer = infoOverlay.getAttribute("context-hub-visible-timer"); //time idle before hiding contexthub
    }

    throwWebsocketEvent(name, data){
        // Prepend events from websocket with 'websocket-' and forward to main event element, document
        var fullName = "websocket-" + name;
        var event = new CustomEvent(fullName, {'detail': data});
        this.eventElement.dispatchEvent(event);
    }

    addWebsocketEventListeners(){
        console.log('[WebsocketDemoMain] Adding websocket events');

        // Listen for websocket messages
        this.websocket.on("message", (eventData) => {
            if(eventData._topic === "Reset mBox"){
                console.info('[WebsocketDemoMain] "Reset mbox" event received');
                // If user presence is not unknown - ie. there IS a user presence
                if(!this.up.isUnknown()) {
                    // Pass the event along ...
                    this.throwWebsocketEvent('reset', eventData);
                }
            }
            else if (eventData._topic === "Found face"){
                console.info('[WebsocketDemoMain] "Found face" event received');
                //if there is at least one prediction
                if (eventData._extendedData.predictions.length > 0) {
                    this.throwWebsocketEvent('face-data-received', eventData);
                }
            }
            else if(eventData._topic === "blob") {
                this.throwWebsocketEvent('incoming-blob', eventData);
            }
            else if (eventData.type === "close"){
                if(!this.ignoreClose) {
                    this.reconnectSocket();
                }
            }
            else if(eventData.type === "open"){
                this.socketConnected();
            }
        });
    }

    addClassEventListeners(){
        // Add EventListeners to the document element to handle websocket events
        this.eventElement.addEventListener('websocket-reset', (e) => {
            console.info('[WebsocketDemoMain] "websocket-reset" event handled');
            this.reset();
        });

        //direct to websocket success events
        this.eventElement.addEventListener('websocket-face-data-received', (e) => {
            console.info('[WebsocketDemoMain] "websocket-face-data-received" event handled');
            var faceData = this.getFocalFaceData(e.detail);
            this.appendSimpleSensorData(faceData);
            this.updateSettings(faceData);
        });

        this.eventElement.addEventListener('websocket-incoming-blob', (e) => {
            // Display incoming blob data to canvas element
            var data = e.detail._extendedData.imageData;
            var dataType = e.detail._extendedData.dataType;
            var blob = this.b64toBlob(data, dataType, 512);
            document.getElementById('canvas').renderImage(blob);
        });
    }

    appendSimpleSensorData(data) {
        // Add data from SimpleSensor websocket event to log element on page
        var dataDiv = document.getElementById('log-data');
        dataDiv.innerHTML += '<br><br>' + JSON.stringify(data);
    }

    throwInterfaceEvent(eventName, attributes) {
        // Prepend 'interface-' to events pertaining to the interface elements; dispatch it.
        var customEventName = "interface-" + eventName;
        var aEvent = new CustomEvent(customEventName, {'detail': attributes});
        this.eventElement.dispatchEvent(aEvent);
    }

    addInterfaceEventListeners() {
        // Add EventListeners to the document element to handle interface events
        this.eventElement.addEventListener('interface-smartad-update', (e) => {
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

    b64toBlob(b64Data, contentType, sliceSize) {
        // Convert base64 string to a blob, given string, MIME, and slice size
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
                }
            }
        }
    }

    reset(){
        console.log('[WebsocketDemoMain] Reset');
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

    hideContextHubBar(){
        // Animate hiding top bar with UserPresence data
        this.contextHubVisible = !this.contextHubVisible;
        $(".contexthub-container").animate({"top":"-4.175rem"}, 1000);
    }

    showContextHubBar(){
        // Animate showing top bar with UserPresence data
        this.contextHubVisible = !this.contextHubVisible;
        $(".contexthub-container").animate({"top":"0rem"}, 1000);

        // Set timer to hide it again, it is hidden by default
        clearTimeout(this.contextHubHideTimer);
        this.contextHubHideTimer = setTimeout(this.hideContextHubBar.bind(this), this.contextHubVisibleTimer*1000);
    }

    hideInfo(){
        // Hide info overlay showing tech used to build demo
        this.infoVisible = !this.infoVisible;
        $("#infoContainer").animate({"opacity":"0"}, 1000);
    }

    showInfo(){
        // Show info overlay
        this.infoVisible = !this.infoVisible;
        $("#infoContainer").animate({"opacity":"1"}, 1000);
    }
    
    addInterfaceInteractions(){
        // Add EventListeners to interface element click events
        document.getElementById("contextHubHideArea").addEventListener("click", () => {
            if(this.contextHubVisible){
                this.hideContextHubBar();
            }
            else{
                this.showContextHubBar();
            }
        });

        document.getElementById("infoButtonContainer").addEventListener("click", () => {
            if(this.infoVisible){
                this.hideInfo();
            }
            else{
                this.showInfo();
            }
        });

        document.getElementById('canvas').addEventListener("click", () => {
           if(self.SHOW_DISPLAY){
                this.websocket.send('close-stream', {
                    _topic: 'close-stream',
                    _sender: 'smart-ads',
                    _recipients: ['camCollectionPoint'],
                    _extraData: {code: 0}
                });
               self.SHOW_DISPLAY = !self.SHOW_DISPLAY;
               $('#canvas, #video').animate({'opacity':'0'}, 1000);
           }
           else{
                this.websocket.send('open-stream', {
                    _topic: 'open-stream',
                    _sender: 'smart-ads',
                    _recipients: ['camCollectionPoint'],
                    _extraData: {code: 0}
                });
               self.SHOW_DISPLAY = !self.SHOW_DISPLAY;
               $('#canvas, #video').animate({'opacity':'1'}, 1000);
           }
        });
    }

    addCanvasBlobRender(){
        // Add blob render function to canvas
        HTMLCanvasElement.prototype.renderImage = (blob) => {

            var ctx = this.getContext('2d');
            var img = new Image();

            img.onload = function(){
                ctx.drawImage(img, 0, 0)
            };

            img.src = window.URL.createObjectURL(blob);
        };
    }
}