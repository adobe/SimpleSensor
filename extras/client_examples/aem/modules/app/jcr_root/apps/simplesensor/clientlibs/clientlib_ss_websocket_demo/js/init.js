
$(function () {
    'use strict';
    window.SimpleSensor = window.SimpleSensor || {};
    window.SimpleSensor.WebsocketClientDemo = window.SimpleSensor.WebsocketClientDemo || new Promise(function (resolve, reject) {
            window.SimpleSensor.WebsocketClientDemo = WebsocketDemoMain;
            resolve(window.SimpleSensor.WebsocketClientDemo);
        });
});