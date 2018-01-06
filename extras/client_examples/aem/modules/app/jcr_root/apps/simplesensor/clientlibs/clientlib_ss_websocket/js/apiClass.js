class API{

    constructor (eventElement, apiChoice){
        this.eventElement = eventElement;
        this.apiChoice = apiChoice;
        this.maleConfidence = "unknown";
        this.femaleConfidence = "unknown";
        this.glassesConfidence = "unknown";
        this.beardConfidence = "unknown";
        this.age = "unknown";
        this.apiHitCounter = 0;
    }

    get data(){
        return {
            maleConfidence: this.maleConfidence,
            femaleConfidence: this.femaleConfidence,
            glassesConfidence: this.glassesConfidence,
            beardConfidence: this.beardConfidence,
            age : this.age
        }
    }

    clearData(){
        this.maleConfidence = "unknown";
        this.femaleConfidence = "unknown";
        this.glassesConfidence = "unknown";
        this.beardConfidence = "unknown";
        this.age = "unknown";
    }

    updateAdobeData(data){
        if(data !== undefined) {
            this.maleConfidence = data.male.confidence;
            this.femaleConfidence = data.female.confidence;
            this.glassesConfidence = data.glasses.confidence;
            this.beardConfidence = data.beard.confidence;
        }
    }

    updateAzureData(data){
        if(data[0] !== undefined){
            console.log('data: ', data);
            this.maleConfidence = data[0].faceAttributes.gender === "male"?1:0;
            this.femaleConfidence = 1 - this.maleConfidence;
            this.age = data[0].faceAttributes.age || this.age || "unknown";
            this.beardConfidence = data[0].faceAttributes.facialHair.beard;
            console.log('beard conf 1: ', this.beardConfidence);
            this.glassesConfidence = data[0].faceAttributes.glasses === "ReadingGlasses"?1:0;
            
        }
    }

    buildAdobeAPI(url){
        this.adobeUrl = url;
    }

    buildAzureAPI(params, url, contentType, key){
        this.azureParams = params;
        this.azureUrl = url;
        this.azureContentType = contentType;
        this.azureKey = key;
    }

    sendAzureRequest(blob) {
        //increment api hit counter
        this.apiHitCounter++;
 
        //update counter element
        $('#apiHitCount').text(this.apiHitCounter.toString());

        var _this = this;

        return new Promise(function (resolve, reject) {

            console.debug("Azure API Class: sending image buffer started");

            $.ajax({
                url: _this.azureUrl + $.param(_this.azureParams),
                beforeSend: function (xhrObj) {
                    // Request headers
                    xhrObj.setRequestHeader("Content-Type", _this.azureContentType);
                    xhrObj.setRequestHeader("Ocp-Apim-Subscription-Key", _this.azureKey);
                },
                processData: false,
                type: "POST",
                data: blob
            })
                .done(function (data) {

                    resolve(data);

                })
                .fail(function (e) {

                    reject(e);

                });
        });
    }

    sendAdobeRequest(blob) {
        var _this = this;

        return new Promise(function (resolve, reject) {

            console.debug("Adobe API Class: sending image buffer started");

            var formData = new FormData();
            formData.append("queryImage", blob);

            $.ajax({
                url: _this.adobeUrl,
                processData: false,
                type: "POST",
                contentType: false,
                data: formData
            })
                .done(function(data) {

                    resolve(data);

                })
                .fail(function(e) {

                    reject(e);

                });
        });
    }


    //Throw interface events, used to update interface
    throwAPIEvent(eventName, attributes) {

        var customEventName = "api-" + eventName;

        console.debug("API Class: dispatching event " + customEventName);

        var aEvent = new CustomEvent(customEventName, {'detail': attributes});
        console.log('event before dispatch: ', aEvent);

        this.eventElement.dispatchEvent(aEvent);
    }

    pushAPIRequest(blob){

        var _this = this;

        this.clearData();

         if(this.apiChoice === 1){ //Azure
        
             this.sendAzureRequest(blob).then(function(data){
                 _this.updateAzureData(data);
                 _this.throwAPIEvent('azure-data-received-success', _this.data);
             }).catch(function(e) {
                 _this.throwAPIEvent('azure-data-received-failure', _this.data);
             })
        
         }else if(this.apiChoice === 0){ //Adobe
        
             this.sendAdobeRequest(blob).then(function(data){
                 _this.updateAdobeData(data);
                 _this.throwAPIEvent('adobe-data-received-success', _this.data);
             }).catch(function(e) {
                 _this.throwAPIEvent('adobe-data-received-failure', _this.data);
             })
        
         }

//        this.sendAdobeRequest(blob).then(
//
//            function(data) {
//
//                _this.updateAdobeData(data);
//
//                _this.sendAzureRequest(blob).then(
//
//                    function(data) {
//
//                        _this.updateAzureData(data);
//
//                        _this.throwAPIEvent('all-data-received-success', _this.data);
//
//                    }
//                ).catch(
//                    function(e) {
//                        _this.throwAPIEvent('azure-data-received-failure', e);
//
//                    }
//                )
//
//            }
//        ).catch(
//            function(e) {
//
//                _this.throwAPIEvent('adobe-data-received-failure', e);
//
//            }
//        )
    }
}