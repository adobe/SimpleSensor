
$(function () {
    'use strict';
    var infoOverlay = document.getElementById("infoOverlay");
    var method = infoOverlay.getAttribute("smart-ad-method");
    window.CEC = window.CEC || {};
    window.CEC.Screen = window.CEC.Screen || new Promise(function (resolve, reject) {
            if(method === "motionDetection") {
                resolve(new MotionDetectionMain());
            }
            else if(method === "websocket") {
                resolve(new WebsocketMain());
            }
        });
});