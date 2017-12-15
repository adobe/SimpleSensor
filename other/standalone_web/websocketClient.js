class WebsocketClient {
    constructor(host,port) {
        self = this;
        this._host = host;
        this._port = port;
        this._messageEventHandlers = []

        //connect to websocket and start to listen
        this._websocket = new WebSocket("ws://"+this._host+":"+this._port);

        this._websocket.addEventListener('open',function (event) {
            console.debug("websocket to " + self._host + " opened" );
        });

        this._websocket.addEventListener('message' ,function (event) {
            self.dispatch("message",JSON.parse(event.data))
        });
      };

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
        }        
    }
  }