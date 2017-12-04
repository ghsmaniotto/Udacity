// Map's data
var map;
var infowindow;
var markersList = [];
var defaultLocation = {
    lat: -27.455982,
    lng: -53.93018
};

// Wikipedia's data
const WIKI_API_URL = "https://en.wikipedia.org/w/api.php";

// Foursquare's data
const FOURSQUARE_API_URL ="https://api.foursquare.com/v2/venues/search";
const CLIENT_ID = 'ODA5SOZFHKGTQF2GZ2FYPTURKBO1KC1F2QYMTVTCAD2PF5FM'
const CLIENT_SECRET = 'OIVBCTQFEYIV2KZTI25WJ1MRLWSZEQWAMVOUST2XN4LNIUUJ'

// Knockout's data
var viewModel = new PlaceListViewModel();
ko.applyBindings(viewModel);

/* -----------------------------------------------------------------
                        Knockout JS
-------------------------------------------------------------------- */

/**
* @description Add ko.observable to a marker
* @param {google.maps.Marker} marker - Marker of a specific place
*/
function Place(marker) {
    this.marker = ko.observable(marker);
};

/**
* @description Knockout View Model
    This class describe all functions and variables to knockout
    will use in the app
*/
function PlaceListViewModel() {
    // Data
    var self = this;
    self.places = ko.observableArray();
    self.filter = ko.observable();
    self.foursquare_checkins_count = ko.observable();
    self.foursquare_users_count = ko.observable();
    self.foursquare_tip_count = ko.observable();

    /**
    * @description Add an place(item) to the places list(observable array)
    * @param {google.maps.Marker} marker - Map's marker
    */
    self.addPlace = function (marker) {
        self.places.push(new Place(marker));
    };

    /**
    * @description Display an info window into specific marker
        The content of the info window is a Foursquare statistic
        about the specific place
    * @param {place} title - The title of the book
    */
    self.showInfoWindow = function(place){
        // Add a listener to animmate the marker when clicked
        var timeout = 1400;
        place.marker().setAnimation(google.maps.Animation.BOUNCE);
        window.setTimeout(function () {
            place.marker().setAnimation(null);
        }, timeout);
        // Set the lat,lng of the place
        var latlng = 
            place.marker().position.lat().toString() +
            "," + place.marker().position.lng().toString();
        // Get the venues response of foursquare and set the infowindow content
        var foursquare_url = getFoursquareDataFor(latlng, place.marker().title);
        // Use Ajax to request the foursquare data
        $.ajax({
            type: 'GET',
            url: foursquare_url,
            dataType: 'jsonp',
            success: (reqResult) => {
                // In success case, show the foursquare content
                if (reqResult.meta &&
                    reqResult.meta.code === 200 &&
                    reqResult.response.venues &&
                    reqResult.response.venues[0]) {
                    infowindow.setContent(
                        `<div><h3>${place.marker().title}</h3></div>
                        <div><h4>Foursquare info's</h4></div>
                        <div><p>Checkins Count: <span data-bind="text: foursquare_checkins_count">${reqResult.response.venues[0].stats.checkinsCount}</span> </p></div>
                        <div><p>Users Count: <span data-bind="text: foursquare_users_count">${reqResult.response.venues[0].stats.usersCount}</span> </p></div>
                        <div><p>Tip Count: <span data-bind="text: foursquare_tip_count">${reqResult.response.venues[0].stats.tipCount}</span> </p></div>`
                    );
                } else {
                    infowindow.setContent(
                        `<div> <h4>${place.marker().title}</h4></div>
                        <div"><h6>The Foursquare data can't be found for this place.</h6></div>`);
                }
            },
            error: () => {
                infowindow.setContent(
                    `<div> <h4>${place.marker().title}</h4></div>
                        <div><h6>The Foursquare data can't be found for this place.</h6></div>`);
            }
        });
        infowindow.open(map, place.marker());
    };

    /**
    * @description Filter the places according to gived place name
    */
    self.filteredItems = ko.computed(function () {
        var filter = self.filter();
        if (!filter) {
            // Set visible the markers when filter is empty
            self.places().forEach(place => place.marker().setMap(map));
            return self.places();
        } else {
            // Return filtered markers
            return ko.utils.arrayFilter(self.places(), function (place) {
                if (place.marker().title.includes(filter)){
                    // Display the filtered marker
                    place.marker().setMap(map);
                } else {
                    // Hidden the non filtered marker
                    place.marker().setMap(null);
                }
                // Return the filtered markers
                return place.marker().title.includes(filter);
            });
        }
    });

};
// End Knockout section

/* -----------------------------------------------------------------
                        Google maps API
-------------------------------------------------------------------- */
/**
    * @description Function to initialize the Google maps
*/
function initMap() {
    // Constructor creates a new map
    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultLocation,
        zoom: 16
    });
    // Create a infowindow to show markers content
    infowindow = new google.maps.InfoWindow();

    /**
    * @description This method will put 20 markers in map according a radius from
            the map start location and type of points (store, restaurants, ..)
            This method call an callback method to manage the response of request
    * @param {map} map - Map's marker
    */
    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch({
        location: defaultLocation,
        radius: 500,
        type: ['store']
    }, callback);

};

/**
    * @description  This is a google.maps.places.PlacesService callback function
        This method will create a marker for each selected point in PlacesService()
*/
function callback(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            markersList.push(createMarker(results[i]));
        }
    }
};

/**
 * @description This method creates a marker into the map.
 The map, position of the marker (lat, lng) and title are defined.
 The complete list of parameters to create a marker is available in
 https://developers.google.com/maps/documentation/javascript/3.exp/reference?hl=pt-br#MarkerOptionsThis is a google.maps.places.PlacesService callback function
 */
function createMarker(place) {
    
    // Get the marker location
    var placeLoc = place.geometry.location;
    var newIcon = makeMarkerIcon("FF7400")
    // Creates a marker
    var marker = new google.maps.Marker({
        map: map,
        icon: newIcon,
        animation: google.maps.Animation.DROP,
        position: placeLoc,
        title: place.name
    });
    // Add a listener to show an infowindow when marker is clicked
    addListenerInfoWindow(map, marker, infowindow);
    // Add a listener to mouseover
    addListenerMouseover("5bc0de", marker);
    // Add a listener to mouseout
    addListenerMouseout("FF7400", marker);
    // Add the marker to the view model
    viewModel.addPlace(marker);
    return marker;
};

/**
 * @description  Add a listener to show an infowindow when marker is clicked
 * @param {google.maps.Map} map - Google Maps map
 * @param {google.maps.marker} marker - Specific marker to add listener
 * @param {google.maps.InfoWindow} infowindow - The map info window
 */
function addListenerInfoWindow(map, marker, infowindow) {
    return marker.addListener(
        'click',
        function () {
            // To animmate the marker when clicked
            var timeout = 1400;
            marker.setAnimation(google.maps.Animation.BOUNCE);
            window.setTimeout(function () {
                marker.setAnimation(null);
            }, timeout);
            // Get foursquare data about the point
            // Set the lat,lng of the place
            var latlng =
                marker.position.lat().toString() +
                "," + marker.position.lng().toString();
            // Get the venues response of foursquare and set the infowindow content
            var foursquare_url = getFoursquareDataFor(latlng, marker.title);
            // Use Ajax to request the foursquare data
            $.ajax({
                type: 'GET',
                url: foursquare_url,
                dataType: 'jsonp',
                success: (reqResult) => {
                    // In success case, show the foursquare content
                    if (reqResult.meta &&
                        reqResult.meta.code === 200 &&
                        reqResult.response.venues &&
                        reqResult.response.venues[0]) {
                        infowindow.setContent(
                        `<div><h3>${marker.title}</h3></div>
                        <div><h4>Foursquare info's</h4></div>
                        <div><p>Checkins Count: <span data-bind="text: foursquare_checkins_count">${reqResult.response.venues[0].stats.checkinsCount}</span> </p></div>
                        <div><p>Users Count: <span data-bind="text: foursquare_users_count">${reqResult.response.venues[0].stats.usersCount}</span> </p></div>
                        <div><p>Tip Count: <span data-bind="text: foursquare_tip_count">${reqResult.response.venues[0].stats.tipCount}</span> </p></div>`
                        );
                    } else {
                        infowindow.setContent(
                            `<div> <h4>${marker.title}</h4></div>
                            <div"><h6>The Foursquare data can't be found for this place.</h6></div>`);
                    }
                },
                error: () => {
                    infowindow.setContent(
                        `<div> <h4>${marker.title}</h4></div>
                        <div><h6>The Foursquare data can't be found for this place.</h6></div>`);
                }
            });
            // Display the infowindow when the button is clicked
            infowindow.open(map, marker);
    });
};

/**
 * @description  Add a listner to animate the marker when it is clicked
 * @param {google.maps.marker} marker - Specific marker to add listener
 */
function addListenerAnimation(marker) {
    return marker.addListener(
        'click',
        function () {
            // Set the infowindow content
            if (this.getAnimation() !== null){
                this.setAnimation(null);
            } else {
                this.setAnimation(google.maps.Animation.BOUNCE);
            }
        });
};

/**
    * @description  Creates a new marker with defined color
    * @param {String} makerColor - String that contains the color 
        Must be in the format -> FFFAAA
*/
function makeMarkerIcon(markerColor) {
    var makerImage = new google.maps.MarkerImage(
        "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + markerColor,
        new google.maps.Size(31, 54),
        new google.maps.Point(0, 0),
        new google.maps.Point(30, 54),
        new google.maps.Size(31, 54),
    );
    return makerImage;
}; 

/**
 * @description  Add a listner to change the marker color
 *   when the mouse is over the marker
 * @param {String} color - Marker's color formatted as -> AAFFAA
 * @param {google.maps.marker} marker - Specific marker to add listener
 */
function addListenerMouseover(color, marker){
    return marker.addListener('mouseover', function(){
        this.setIcon(makeMarkerIcon(color));
    })
};
/**
 * @description  Add a listner to change the marker color
 *   when the mouse is out the marker
 * @param {String} color - Marker's color formatted as -> AAFFAA
 * @param {google.maps.marker} marker - Specific marker to add listener
 */
function addListenerMouseout(color, marker) {
    return marker.addListener('mouseout', function(){
        this.setIcon(makeMarkerIcon(color));
    })
}

function mapErrorHandler(err){
    $('#map').html(`<div class="mt-5"><div class="row justify-content-center mt-5 pt-5"><h1 class="mt-5 pt-5"><em>The Google Maps's map can't be loaded :/</em></h1></div></div>`);
}
// End Google API section

/* -----------------------------------------------------------------
                        Foursquare's API
-------------------------------------------------------------------- */
/**
    * @description  This function creates a url to get the foursquare data for a specific point
        According to these parementers, the request for the foursquare api
        returns some data about this place/point
    * @param {String} point_latlng - Lat,lng of the place.
        Must be formated as -> (lat,lng)
    * @param {String} point_name - Specific marker to add listener
*/
function getFoursquareDataFor(point_latlng, point_name) {
    var foursquare_url = FOURSQUARE_API_URL;
    return foursquare_url += '?' + $.param({
        "ll": point_latlng,
        "client_id": "ODA5SOZFHKGTQF2GZ2FYPTURKBO1KC1F2QYMTVTCAD2PF5FM",
        "client_secret": "OIVBCTQFEYIV2KZTI25WJ1MRLWSZEQWAMVOUST2XN4LNIUUJ",
        "v": "20171202",
        "radius": "1",
        "intent": "match",
        "name": point_name
    });
}
