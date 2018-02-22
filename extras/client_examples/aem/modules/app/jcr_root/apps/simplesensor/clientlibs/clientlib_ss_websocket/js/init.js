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
 * Init
 * This is overly complex but was needed for a complex application.  This promise is basically just a event to let us know the lib is loaded.
 * I think this is dumb in this simple solution
 */
$(function () {
    'use strict';
    window.SimpleSensor = window.SimpleSensor || {};
    window.SimpleSensor.WebsocketClient = window.SimpleSensor.WebsocketClient || new Promise(function (resolve, reject) {
            window.SimpleSensor.WebsocketClient = WebsocketClient;
            resolve(window.SimpleSensor.WebsocketClient);
        });
});