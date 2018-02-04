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
 */
package com.simplesensor.servlets;

import com.day.crx.JcrConstants;
import org.apache.felix.scr.annotations.sling.SlingServlet;
import org.apache.sling.api.SlingConstants;
import org.apache.sling.api.SlingHttpServletRequest;
import org.apache.sling.api.SlingHttpServletResponse;
import org.apache.sling.api.resource.Resource;
import org.apache.sling.api.resource.ValueMap;
import org.apache.sling.api.servlets.SlingSafeMethodsServlet;
import org.apache.sling.commons.json.JSONException;
import org.apache.sling.commons.json.io.JSONWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.Map.Entry;
import javax.servlet.ServletException;
import java.io.IOException;

@SuppressWarnings("serial")
@SlingServlet(
        resourceTypes = "sling/servlet/default",
        methods = {"GET"},
        selectors = {"screenlocation"},
        extensions = {"json"})
public class LocationInfoServlet extends SlingSafeMethodsServlet {
    private static final Logger log = LoggerFactory.getLogger(LocationInfoServlet.class);

    @Override
    protected void doGet(final SlingHttpServletRequest request,final SlingHttpServletResponse response) throws ServletException, IOException {
        //does the path have location data?
        log.debug("getting the location data from content on path " + request.getResource().getPath());
        final Resource locationResource = getFirstLocation(request.getResource());

        //does the path have location data?
        log.debug("getting the location data from content on path " + locationResource.getPath());
        ValueMap vm = locationResource.getValueMap();
        String nodeType = vm.get(SlingConstants.PROPERTY_RESOURCE_TYPE,"");
        log.debug("looking for location node and found nodeType " + nodeType);

        JSONWriter w = new JSONWriter(response.getWriter());
        response.setContentType("application/json");

        if( locationResource != null ){
            try {
                w.object();
                for(Entry<String, Object> e : vm.entrySet()) {
                    String key = e.getKey();
                    Object value = e.getValue();
                    w.key(key).value(value);
                }
                w.endObject();
            } catch (JSONException e) {
                log.error("Error creating JSON for location info request", e);
                response.sendError(500);
            }
        }else{
            try{
                w.object();
                w.key("error").value("Location data not found");
                w.key("message").value("location info not found for path " + request.getResource().getPath());
                w.endObject();
            } catch (JSONException e) {
                log.error("Error creating JSON for location info request", e);
                response.sendError(500);
            }

            log.error("Error creating JSON for location info request.  No location data was found on path " + request.getResource().getPath());
            response.sendError(500);
        }

    }

    private Resource getFirstLocation(Resource targetResource){
        if(targetResource != null){
            Resource resourceContent = targetResource.getChild(JcrConstants.JCR_CONTENT);
            ValueMap vm = resourceContent.getValueMap();
            String nodeType = vm.get(SlingConstants.PROPERTY_RESOURCE_TYPE,"");
            log.debug("looking for location node and found nodeType " + nodeType);

            if( nodeType.equalsIgnoreCase("screens/core/components/location") ){
                return resourceContent;
            }else{
                try{
                    return getFirstLocation(targetResource.getParent());
                }catch (Exception e){
                    return null;
                }
            }
        }else{
            return null;
        }
    }
}
