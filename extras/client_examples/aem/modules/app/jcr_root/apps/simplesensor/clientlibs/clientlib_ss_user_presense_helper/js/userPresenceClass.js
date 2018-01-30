/*
 *  Copyright 2018 Adobe Systems Incorporated
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *  not my circus, not my monkeys
 *
 *  Created by: David bEnGe at some time in 2016
 *  Helps us to get the first Location under a Device path in AEM screens
 *  just take the devicepath from the screens client lib and then take that path and do a get on it with .screenlocation.json on that request
 *  this will return either an error or a json serialized version of that location node.  Which is where we store some data for tuning client side applications per location
 *
 * Created : sometime in 2016
 * Author : David bEnGe
 *
 * SimpleSensorUserPresenceUpdateHelper
 * helper for us to use to update the simplesensor-user-presence store
 */

class SimpleSensorUserPresenceUpdateHelper{

    constructor(contextHub, minConfidence, genderDiff){
        this.store = contextHub.getStore("simplesensor_user_presence_store");
        this.minConfidence = minConfidence;
        this.genderDiff = genderDiff;
    }

    /*
     * Smart Ad is a target use case where us use the ContextHub to drive what is displayed.
     * The ContextHub is populated based on IOT sensors and Computer Vision logic
     */

    /**
     * updates the user ContextHub user presence store
     *
     * console check ContextHub.getStore("simplesensor_user_presence").getItem("sex");
     *
     * @param {object} params  {emotions:{Object {"":decimal}, sex:"",glasses:"",facialHair:"",age:"",garmentShapeClassifierTop:"",gsctDominantColor:""gsctStdColor:"",gsctSleeves:"",gsctLength:"",
         *     gsctCollarShape:"",gsctFit:"",ageRangeMin:"",ageRangeMax:"",ethnicity:"",garmentShapeClassifierBottom:"",gscbDominantColor:"",
         *     gscbStdColor:"",gscbSleeves:"",gscbLength:"",gscbFit:"",gscbCategory:""}
         */
    updateUserPresenceStore(params){
            if (params.gender !== "undefined") {
                this.store.updateGender(params.gender);
            }

            if (params.age !== "undefined") {
                this.store.updateAge(params.age);
            }

            if (params.facialHair !== "undefined") {
                this.store.updateFacialHair(params.facialHair);
            }

            if (params.glasses !== "undefined") {
                this.store.updateGlasses(params.glasses);
            }
    };

    //Set the gender values in presence store (filtered by case)
    //Return value if changed, false if no change
    setGender(femaleConfidence, maleConfidence) {
        var newGenderVal = "Unknown";

        /* get the selected sex */
        var oldGenderVal = this.store.getItem("gender");

        var female = parseFloat(femaleConfidence);
        var male = parseFloat(maleConfidence);

        if(female >= this.minConfidence || male >= this.minConfidence && !(female >= this.minConfidence && male >= this.minConfidence)){
            var diff = female - male;

            var absDiff = Math.abs(diff);

            if (absDiff >= this.genderDiff){
                if (diff >= 0){
                    newGenderVal = "female";
                } else {
                    newGenderVal = "male";
                }
            }
        }

        if(oldGenderVal !== newGenderVal){
            console.log("Setting Gender from "+ oldGenderVal + " to "+ newGenderVal);
            this.updateUserPresenceStore({gender:newGenderVal});
            return newGenderVal;
        }
        else {
            console.log("Gender values have not changed "+ oldGenderVal + " : "+ newGenderVal);
            return false;
        }
    }

    getParam(param){
        return this.store.getItem(param);
    }

    isUnknown(){
        return (this.getParam("glasses") === "Unknown" &&
                this.getParam("age") === "Unknown" &&
                this.getParam("beard") === "Unknown" &&
                this.getParam("beard") === "Unknown");
    }

    //Set the glasses values in presence store (filtered by case)
    //Return value if changed, false if no change
    setGlasses(glassesConfidence) {
        var newGlassesVal = "Unknown";
        /* get the selected glasses val */
        var oldGlassesVal = this.store.getItem("glasses");

        var glasses = parseFloat(glassesConfidence);

        if(glasses >= this.minConfidence){
            newGlassesVal = "glasses";
        } else {
            newGlassesVal = "no glasses";
        }

        if(oldGlassesVal !== newGlassesVal){
            console.log("Setting Glasses from "+ oldGlassesVal + " to "+ newGlassesVal);
            this.updateUserPresenceStore({glasses:newGlassesVal});
            return newGlassesVal;
        }
        else {
            console.log("Glasses values have not changed "+ oldGlassesVal + " : "+ newGlassesVal);
            return false
        }
    }

    //Set the age values in presence store (filtered by case)
    //Return value if changed, false if no change
    setAge(age, smoother) {

        var bigChange = false;

        var newAgeVal = "Unknown";

        var age = parseFloat(age);

        var ageNaN = isNaN(age);

        var oldAgeVal = parseFloat(this.store.getItem("age"));

        var oldAgeNaN = isNaN(oldAgeVal);

        if(oldAgeNaN == true){

            oldAgeVal = this.store.getItem("age");

        }

        if( ageNaN == false ) {

            var ageYears = parseFloat(age);

            if(ageYears >= 65){
                newAgeVal = 65;
            }else if (ageYears < 20) {
                newAgeVal = 20
            } else {
                newAgeVal = Math.trunc(ageYears);
            }

            if( oldAgeNaN == false ){

                var diff = newAgeVal - oldAgeVal;

                var absDiff = Math.abs(diff);

                if(absDiff >= smoother){
                    bigChange = true;
                }
            } else {

                bigChange = true;
            }

        }

        if(bigChange == false && ageNaN == false){
            console.log("Setting Age from "+ oldAgeVal + " to "+ newAgeVal);
            this.updateUserPresenceStore({age:newAgeVal});
            return false;
        } else if (oldAgeVal !== newAgeVal){
            console.log("Setting Age from "+ oldAgeVal + " to "+ newAgeVal);
            this.updateUserPresenceStore({age:newAgeVal});
            return newAgeVal;
        }
        else {
            console.log("Age values have not changed "+ oldAgeVal + " : "+ newAgeVal);
            return false;
        }
    }

    //Set the facial hair values in presence store (filtered by case)
    //Return value if changed, false if no change
    setFacialHair(beardConfidence) {
        var newFacialHairVal = "Unknown";
        /* get the selected glasses val */
        var oldFacialHairVal = this.store.getItem("facialHair");

        var beard = parseFloat(beardConfidence);
        
        console.log('beard conf; ', beard);

        if(beard >= this.minConfidence){
            newFacialHairVal = "beard";
        } else {
            newFacialHairVal = "no beard";
        }

        if(oldFacialHairVal !== newFacialHairVal){
            console.log("Setting Facial Hair from "+ oldFacialHairVal + " to "+ newFacialHairVal);
            this.updateUserPresenceStore({facialHair:newFacialHairVal});
            return newFacialHairVal;
        }
        else {
            console.log("Facial Hair values have not changed "+ oldFacialHairVal + " : "+ newFacialHairVal);
            return false;
        }

    }
}