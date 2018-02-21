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
 * Created : sometime in 2017 around q4
 * Author : David bEnGe
 *
 * Creates new class named WebsocketClient for use to connect via websocket to a SimpleSensor
 *
 * this is a simple local webclient for SimpleSensor.
 * After you create the object WebsocketClient(localhost,13254)   or whatever, you can subscribe to messages off this new object for example
 * var ssWs = new WebsocketClient(localhost,13254);
 * ssWs.on("message",function(eventData){ //do something more interesting here });
 *
 * This clientlib is pretty lite.  It basically only handles three events (message,open,close)
 *
 */
class WebsocketClient {
    constructor(host, port) {
        console.info('[WebsocketClient] Creating client for Simple Sensor');
        this._host = host;
        this._port = port;
        this._messageEventHandlers = [];
        this.connect();
    };

    connect(){
        console.info('[WebsocketClient] Connecting client to Simple Sensor');

        //connect to websocket and start to listen
        this._websocket = new WebSocket("ws://"+this._host+":"+this._port);

        this._websocket.addEventListener('open', (event) => {
            console.debug("websocket to " + self._host + ":" + self._port + " opened" );
            // console.log('opened event: ', event);
            this.dispatch("open", event);
        });

        this._websocket.addEventListener('close', (event) => {
            console.debug("websocket to " + self._host + ":" + self._port + " closed" );
            // console.log('closed event: ', event);
            this.dispatch("close", event);
        });

        this._websocket.addEventListener('message' , (event) => {
            this.dispatch("message", JSON.parse(event.data))
        });
    }

    reconnect(){
        this.connect();
    }

    on(eventName, handler){
        switch (eventName) {
            case "message":
                return this._messageEventHandlers.push(handler);
        }
    }

    dispatch(eventName,eventData){
        switch (eventName) {
            case "message":
                var handler, i, len, ref;
                for (i = 0;i < this._messageEventHandlers.length; i++) {
                    handler = this._messageEventHandlers[i];
                    setTimeout(handler(eventData), 0);
                }
                break;
            case "close":
                var handler, i, len, ref;
                for (i = 0;i < this._messageEventHandlers.length; i++) {
                    handler = this._messageEventHandlers[i];
                    setTimeout(handler(eventData), 0);
                }
                break;
            case "open":
                var handler, i, len, ref;
                for (i = 0;i < this._messageEventHandlers.length; i++) {
                    handler = this._messageEventHandlers[i];
                    setTimeout(handler(eventData), 0);
                }
                break;
        }
    }

    send(topic, eventData) {
        var msg = {
            type: type,
            data: eventData
        }
        this._websocket.send(JSON.stringify(msg));
    }
}