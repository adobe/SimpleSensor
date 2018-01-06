ContextHub.console.log(ContextHub.Shared.timestamp(), '[loading] contexthub.store clientContext - simplesensor-user-presence');

(function($) {
    'use strict';

    var defaultConfig = {
        maxCount: 20
    };

    /**
     * AAA User Presence store implementation.
     *
     * @constructor
     * @extends ContextHub.Store.PersistedStore
     * @param {String} name - store name
     * @param {Object} config - store config
     */
    var UserPresenceStore = function(name, config) {
        /* initialize store */
        this.config = $.extend({}, true, defaultConfig, config);
        this.init(name, this.config);

        /**
         * Sets updateGender
         * @param {string} gender  [male,female,u]
         */
        this.updateGender = function(gender) {
            if (!this.getItem('gender') || gender) {
                this.setItem('gender', gender);
            }
        };

        /**
         * Sets updateAge
         * @param {decimal} age
         */
        this.updateAge = function(age) {
            if (!this.getItem('age') || age) {
                this.setItem('age', age);
            }
        };

        /**
         * Sets updateEmotions (array)
         * @param {Object} emotions [anger, contempt, disgust, fear, happiness, neutral, sadness, surprise]
         */
        this.updateEmotions= function(emotions) {
            if (!this.getItem('emotions') || emotions) {
                this.setItem('emotions', emotions);
            }
        };
        
        /**
         * Sets updateSmile
         * @param {decimal} smile [decimal, u]
         */
        this.updateSmile = function(smile) {
            if (!this.getItem('smile') || smile) {
                this.setItem('smile', smile);
            }
        };

        /**
         * Sets updateFacialHair (beard length)
         * @param {decimal} facialHair
         */
        this.updateFacialHair = function(facialHair) {
            if (!this.getItem('facialHair') || facialHair) {
                this.setItem('facialHair', facialHair);
            }
        };


        /**
         * Sets updateGlasses
         * @param {string} glasses [noGlasses, readingGlasses, sunglasses, swimmingGoggles]
         */
        this.updateGlasses = function(glasses) {
            if (!this.getItem('glasses') || glasses) {
                this.setItem('glasses', glasses);
            }
        };

        /**
         * Sets updateAgeRangeMin
         * @param {number} range
         */
        this.updateAgeRangeMin = function(range) {
            if (!this.getItem('ageRangeMin') || range) {
                this.setItem('ageRangeMin', range);
            }
        };

        /**
         * Sets updateAgeRangeMax
         * @param {number} range
         */
        this.updateAgeRangeMax = function(range) {
            if (!this.getItem('ageRangeMax') || range) {
                this.setItem('ageRangeMax', range);
            }
        };

        /**
         * Sets ethnicity
         * @param {string} ethnicity  [b,w,a,u]
         */
        this.updateEthnicity = function(ethnicity) {
            if (!this.getItem('ethnicity') || ethnicity) {
                this.setItem('ethnicity', ethnicity);
            }
        };

        /**
         * Sets eye location
         * @param {string} eyeLocation  [f,nf]
         */
        this.updateEyeLocation = function(eyeLocation) {
            if (!this.getItem('eyeLocation') || eyeLocation) {
                this.setItem('eyeLocation', eyeLocation);
            }
        };

        /**
         * Sets mode score
         * @param {string} modeScore  [1-100]  -1 for unknown
         */
        this.updateModeScore = function(modeScore) {
            if (!this.getItem('modeScore') || modeScore) {
                this.setItem('modeScore', modeScore);
            }
        };

        /**
         * Set dominant Color Face
         * @param {string} dominantColorFace  [RGB color 255,0,0]  -1 for unknown
         */
        this.updateDominantColorFace = function(dominantColorFace) {
            if (!this.getItem('dominantColorFace') || dominantColorFace) {
                this.setItem('dominantColorFace', dominantColorFace);
            }
        };

        /**
         * Set garment Shape Classifier Top
         * @param {string} garmentShapeClassifierTop  [shirt,dress]  U for unknown
         */
        this.updateGarmentShapeClassifierTop = function(garmentShapeClassifierTop) {
            if (!this.getItem('garmentShapeClassifierTop') || garmentShapeClassifierTop) {
                this.setItem('garmentShapeClassifierTop', garmentShapeClassifierTop);
            }
        };

        /**
         * Set garment Shape Classifier Top - Dominant color
         * @param {string} gsctDominantColor  [RGB color 255,0,0]  -1 for unknown
         */
        this.updateGsctDominantColor = function(gsctDominantColor) {
            if (!this.getItem('gsctDominantColor') || gsctDominantColor) {
                this.setItem('gsctDominantColor', gsctDominantColor);
            }
        };

        /**
         * Set garment Shape Classifier Top - STD color
         * @param {string} gsctStdColor  [RGB color 255,0,0]  -1 for unknown
         */
        this.updateGsctStdColor = function(gsctStdColor) {
            if (!this.getItem('gsctStdColor') || gsctStdColor) {
                this.setItem('gsctStdColor', gsctStdColor);
            }
        };

        /**
         * Set garment Shape Classifier Top - sleeves
         * @param {string} gsctSleeves  [no-sleeves, short, three_quarter, full]  U for unknown
         */
        this.updateGsctSleeves = function(gsctSleeves) {
            if (!this.getItem('gsctSleeves') || gsctSleeves) {
                this.setItem('gsctSleeves', gsctSleeves);
            }
        };

        /**
         * Set garment Shape Classifier Top - length
         * @param {string} gsctLength  [crop,hips,thigh for shirt short,knee,three_quarter, full for dress]  U for unknown
         */
        this.updateGsctLength = function(gsctLength) {
            if (!this.getItem('gsctLength') || gsctLength) {
                this.setItem('gsctLength', gsctLength);
            }
        };

        /**
         * Set garment Shape Classifier Top - Fabric Texture
         * @param {string} gsctFabricTexture  [crop,hips,thigh for shirt short,knee,three_quarter, full for dress]  U for unknown
         */
        this.updateGsctFabricTexture = function(gsctFabricTexture) {
            if (!this.getItem('gsctFabricTexture') || gsctFabricTexture) {
                this.setItem('gsctFabricTexture', gsctFabricTexture);
            }
        };

        /**
         * Set garment Shape Classifier Top - Collar Shape
         * @param {string} gsctCollarShape  [round, v-shape]  U for unknown
         */
        this.updateGsctCollarShape = function(gsctCollarShape) {
            if (!this.getItem('gsctCollarShape') || gsctCollarShape) {
                this.setItem('gsctCollarShape', gsctCollarShape);
            }
        };

        /**
         * Set garment Shape Classifier Top - Fit
         * @param {string} gsctFit  [loose, regular, tight]  U for unknown
         */
        this.updateGsctFit = function(gsctFit) {
            if (!this.getItem('gsctFit') || gsctFit) {
                this.setItem('gsctFit', gsctFit);
            }
        };


        /**
         * Set garment Shape Classifier Bottom
         * @param {string} garmentShapeClassifierBottom  [pants]  U for unknown
         */
        this.updateGarmentShapeClassifierBottom = function(garmentShapeClassifierBottom) {
            if (!this.getItem('garmentShapeClassifierBottom') || garmentShapeClassifierBottom) {
                this.setItem('garmentShapeClassifierBottom', garmentShapeClassifierBottom);
            }
        };

        /**
         * Set garment Bottom - Dominant color
         * @param {string} gscbDominantColor  [RGB color 255,0,0]  -1 for unknown
         */
        this.updateGscbDominantColor = function(gscbDominantColor) {
            if (!this.getItem('gscbDominantColor') || gscbDominantColor) {
                this.setItem('gscbDominantColor', gscbDominantColor);
            }
        };

        /**
         * Set garment Bottom - STD color
         * @param {string} gscbStdColor  [RGB color 255,0,0]  -1 for unknown
         */
        this.updateGscbStdColor = function(gscbStdColor) {
            if (!this.getItem('gscbStdColor') || gscbStdColor) {
                this.setItem('gscbStdColor', gscbStdColor);
            }
        };

        /**
         * Set garment Shape Classifier Bottom - legs aka sleeves
         * @param {string} gscbSleeves  [no-sleeves, short, three_quarter, full]  U for unknown
         */
        this.updateGscbSleeves = function(gscbSleeves) {
            if (!this.getItem('gscbSleeves') || gscbSleeves) {
                this.setItem('gscbSleeves', gscbSleeves);
            }
        };

        /**
         * Set garment Shape Classifier Bottom - length
         * @param {string} gscbLength  [crop,hips,thigh for shirt short,knee,three_quarter, full for dress]  U for unknown
         */
        this.updateGscbLength = function(gscbLength) {
            if (!this.getItem('gscbLength') || gscbLength) {
                this.setItem('gscbLength', gscbLength);
            }
        };

        /**
         * Set garment Shape Classifier Bottom - Fabric Texture
         * @param {string} gscbFabricTexture  [crop,hips,thigh for shirt short,knee,three_quarter, full for dress]  U for unknown
         */
        this.updateGscbFabricTexture = function(gscbFabricTexture) {
            if (!this.getItem('gscbFabricTexture') || gscbFabricTexture) {
                this.setItem('gscbFabricTexture', gscbFabricTexture);
            }
        };

        /**
         * Set garment Shape Classifier Bottom - Fit
         * @param {string} gscbFit  [loose, regular, tight]  U for unknown
         */
        this.updateGscbFit = function(gscbFit) {
            if (!this.getItem('gscbFit') || gscbFit) {
                this.setItem('gscbFit', gscbFit);
            }
        };

        /**
         * Set garment Shape Classifier Bottom - Category
         * @param {string} gscbCategory  [jeans,short,pants,three_quarter]  U for unknown
         */
        this.updateGscbCategory = function(gscbCategory) {
            if (!this.getItem('gscbCategory') || gscbCategory) {
                this.setItem('gscbCategory', gscbCategory);
            }
        };

        //init
        this.loadDefaults();
        this.announceReadiness();
    };
    ContextHub.Utils.inheritance.inherit(UserPresenceStore, ContextHub.Store.PersistedStore);

    UserPresenceStore.prototype.reset = function() {
        this.reset();
    };

    UserPresenceStore.prototype.loadDefaults = function() {
        this.setItem("gender", "u", {silent: true});
        this.setItem("age", "u", {silent: true});
        this.setItem("facialHair", "u", {silent: true});
        this.setItem("glasses", "u", {silent: true});
        this.setItem("ageRangeMin", "-1", {silent: true});
        this.setItem("ageRangeMax", "-1", {silent: true});
        this.setItem("ethnicity", "U", {silent: true});
        this.setItem("eyeLocation", "U", {silent: true});
        this.setItem("moodScore", "-1", {silent: true}); //1-100
        this.setItem("dominantColorFace", "-1", {silent: true});

        this.setItem("garmentShapeClassifierTop", "U", {silent: true}); //shirt or dress
        this.setItem("gsctDominantColor", "U", {silent: true});
        this.setItem("gsctStdColor", "U", {silent: true});
        this.setItem("gsctSleeves", "U", {silent: true}); //no-sleeves, short, three_quarter, full
        this.setItem("gsctLength", "U", {silent: true}); //crop,hips,thigh for shirt short,knee,three_quarter, full for dress
        this.setItem("gsctFabricTexture", "U", {silent: true}); //TBD
        this.setItem("gsctCollarShape", "U", {silent: true}); //round, v-shape
        this.setItem("gsctFit", "U", {silent: true}); //loose, regular, tight

        this.setItem("garmentShapeClassifierBottom", "U", {silent: true}); //pants
        this.setItem("gscbDominantColor", "U", {silent: true});
        this.setItem("gscbStdColor", "U", {silent: true});
        this.setItem("gscbSleeves", "U", {silent: true}); //no-sleeves, short, three_quarter, full
        this.setItem("gscbLength", "U", {silent: true}); //crop,hips,thigh for shirt short,knee,three_quarter, full for dress
        this.setItem("gscbFabricTexture", "U", {silent: true}); //TBD
        this.setItem("gscbFit", "U", {silent: true}); //loose, regular, tight
        this.setItem("gscbCategory", "U", {silent: true}); //jeans,short,pants,three_quarter
    };

    /* register the store */
    ContextHub.Utils.storeCandidates.registerStoreCandidate(UserPresenceStore, 'simplesensor-user-presence', 10);

}(ContextHubJQ));
