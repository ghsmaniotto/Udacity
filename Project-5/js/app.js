// Map's data
var map;
var infowindow;
var markersList = [];
var trespassos = {
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

function Place(marker) {
    this.marker = ko.observable(marker);
};

function PlaceListViewModel() {
    // Data
    var self = this;
    self.places = ko.observableArray();
    self.filter = ko.observable();
    self.foursquare_checkins_count = ko.observable();
    self.foursquare_users_count = ko.observable();
    self.foursquare_tip_count = ko.observable();

    // Operations
    self.addPlace = function (marker) {
        self.places.push(new Place(marker));
    };

    // Display the info window to specific marker
    self.showInfoWindow = function(place){ 
        // Add content to infowindow
        var latlng = 
            place.marker().position.lat().toString() +
            "," + place.marker().position.lng().toString();
        // Get the venues response of foursquare and set the infowindow content
        var foursquare_url = getFoursquareDataFor(latlng, place.marker().title);
        $.ajax({
            type: 'GET',
            url: foursquare_url,
            dataType: 'jsonp',
            success: (reqResult) => {
                console.log(reqResult);
                if (reqResult.meta &&
                    reqResult.meta.code === 200 &&
                    reqResult.response.venues &&
                    reqResult.response.venues[0]) {
                    infowindow.setContent(
                        `<div><h4>Foursquare info's</h4></div>
                        <div><p>Checkins Count: <span data-bind="text: foursquare_checkins_count">${reqResult.response.venues[0].stats.checkinsCount}</span> </p></div>
                        <div><p>Users Count: <span data-bind="text: foursquare_users_count">${reqResult.response.venues[0].stats.usersCount}</span> </p></div>
                        <div><p>Tip Count: <span data-bind="text: foursquare_tip_count">${reqResult.response.venues[0].stats.tipCount}</span> </p></div>`
                    );
                    self.foursquare_checkins_count(reqResult.response.venues[0].stats.checkinsCount);
                    self.foursquare_users_count(reqResult.response.venues[0].stats.usersCount);
                    self.foursquare_tip_count(reqResult.response.venues[0].stats.tipCount);
                } else {
                    infowindow.setContent(`<div><h4>The Foursquare data can't be open. Sorry. Try another marker :D</h4></div>`);
                }
            },
            error: () => {
                infowindow.setContent(`<div><h4>The Foursquare data can't be open. Sorry. Try another marker :D</h4></div>`);
            }
        });
        infowindow.open(map, place.marker());
    };

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
function initMap() {
    // Constructor creates a new map
    map = new google.maps.Map(document.getElementById('map'), {
        center: trespassos,
        zoom: 16
    });
    // Create a infowindow to show markers content
    infowindow = new google.maps.InfoWindow();

    /* 
        This method will put 20 markers in map according a radius from
        the map start location and type of points (store, restaurants, ..)
        This method call an callback method to manage the response of request
    */
    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch({
        location: trespassos,
        radius: 500,
        type: ['store']
    }, callback);

};

// This is a google.maps.places.PlacesService callback function
// This method will create a marker for each selected point in PlacesService()
function callback(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            markersList.push(createMarker(results[i]));
        }
    }
};

/* 
 This method creates a marker into the map.
 The map, position of the marker (lat, lng) and title are defined.
 The complete list of parameters to create a marker is available in
 https://developers.google.com/maps/documentation/javascript/3.exp/reference?hl=pt-br#MarkerOptions
 */ 
function createMarker(place) {
    // Get the marker location
    var placeLoc = place.geometry.location;
    // Creates a marker
    var marker = new google.maps.Marker({
        map: map,
        position: placeLoc,
        title: place.name
    });
    // Add a listner to show an infowindow when marker is clicked
    addListener(map, marker, infowindow);
    // Add the marker to the view model
    viewModel.addPlace(marker);
    return marker;
};

// Add a listner to show an infowindow when marker is clicked
function addListener(map, marker, infowindow) {
    return marker.addListener(
        'click',
        function () {
            // Set the infowindow content
            infowindow.setContent(marker.title);
            // Display the infowindow when the button is clicked
            infowindow.open(map, marker);
        });
};
// End Google API section

/* -----------------------------------------------------------------
                        Foursquare's API
-------------------------------------------------------------------- */
/* 
    This function creates a url to get the foursquare data for a specific point
    According to these parementers, the request for the foursquare api
        returns some data about this place/point
    Parameters:
        - The point_latlng parameter is a stirng, formated like
            -> point_latlng = (lat,lng)
        - The point_name is a string
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
