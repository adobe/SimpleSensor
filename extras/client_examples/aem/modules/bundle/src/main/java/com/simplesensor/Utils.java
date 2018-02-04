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
 *  Created by David bEnGe on 7/28/16
 */
package com.simplesensor;

import com.day.cq.search.PredicateGroup;
import com.day.cq.search.Query;
import com.day.cq.search.QueryBuilder;
import com.day.cq.search.result.Hit;
import com.day.cq.search.result.SearchResult;
import com.day.crx.JcrConstants;
import org.apache.sling.api.SlingConstants;
import org.apache.sling.api.resource.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.jcr.RepositoryException;
import javax.jcr.Session;
import java.util.HashMap;
import java.util.Map;

public final class Utils {
    private static final Logger logger = LoggerFactory.getLogger(Utils.class);

    private Utils() {
    }

    public static String createNewLocationId(Resource locationResource){
        String locationId = "";
        //we need to add on a location id.  this id is used by the client to create a socket.io namespace for the location
        logger.debug("is createNewLocationId for " + locationResource.getPath());

        Resource location = null;
        boolean idFound = false;
        while (!idFound){
            //make locationId
            locationId = java.util.UUID.randomUUID().toString();

            try{
                //check that its not in use
                location = getLocationByUniqueId(locationId,locationResource.getResourceResolver());
            }catch (RepositoryException rex){
                logger.error(rex.getLocalizedMessage(),rex.getStackTrace());
            }

            if(location == null){
                idFound = true;
            }
        }

        //save it to the resource
        ModifiableValueMap locationValueMap = locationResource.adaptTo(ModifiableValueMap.class);
        locationValueMap.put("locationId",locationId);
        logger.debug("saving new location id to " + SlingConstants.PROPERTY_PATH);
        try{
            locationResource.getResourceResolver().commit();
        }catch (PersistenceException pe){
            logger.error(pe.getLocalizedMessage(),pe.getStackTrace());
        }

        return locationId;
    }

    /***
     * getLocationByUniqueId
     * query to check and see if the new code is unique in the system
     *
     * @param locationId
     * @return Resource or null if not found
     * @throws RepositoryException
     */
    public static Resource getLocationByUniqueId(String locationId,ResourceResolver resourceResolver) throws RepositoryException{
        logger.debug("looking for location by id");

        //Get the current session
        QueryBuilder queryBuilder = resourceResolver.adaptTo(QueryBuilder.class);
        Session session = resourceResolver.adaptTo(Session.class);
        Map map = new HashMap();
        map.put("path", "/content/screens");
        map.put("1_property", "locationId");
        map.put("1_property.value", locationId);
        Query query = queryBuilder.createQuery(PredicateGroup.create(map), session);

        //Get the results of the query
        SearchResult result = query.getResult();

        if(result.getTotalMatches() > 0) {
            for (Hit hit : result.getHits()) {
                //Found a device! Return it
                String path = hit.getPath();

                Resource locationResource = null;
                locationResource = resourceResolver.getResource(path);

                return locationResource;
            }
        }

        return null;
    }
    public static Resource getFirstLocationFromPath(Resource locationResource){
        Resource content = locationResource.getChild(JcrConstants.JCR_CONTENT);

        if(content.isResourceType("screens/core/components/location")){
            return locationResource;
        }else{
            Resource parent = locationResource.getParent();
            if(parent != null){
                return getFirstLocationFromPath(parent);
            }
        }

        return null;
    }
}
