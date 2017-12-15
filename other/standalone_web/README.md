# SimpleSensor - other - standalone web 

This subfolder contains an example of hooking up to the local websocket exposed by this sensor project.

The javascript lib is in websocketClient.js and an example of the implmentation in a page can be found in index.html or inline below. 

```
$(document).ready(function() {
            var testResultsElm = $('#testResults');

            var cecWebsocketClient = new CecWebsocketClient("127.0.0.1",13254);

            cecWebsocketClient.on("message",function(eventData){
                testResultsElm.append(JSON.stringify(eventData));
            });
        });
```
