var map;

var trespassos = {
    lat: -27.455982,
    lng: -53.93018
}

function initMap() {
    // Constructor creates a new map - only center and zoom are required.
    map = new google.maps.Map(document.getElementById('map'), {
        center: trespassos,
        zoom: 16
    });

    var marker = addMarker(trespassos, map, "Tres Passos");
    var infowindow = addInfoWindow(`${marker.getPosition()}`);
   
    addListener(map, marker, infowindow);

    var placeSearchAutoComplete = new google.maps.places.Autocomplete(
        document.getElementById('search-box')
    );
    placeSearchAutoComplete.bindTo('bounds', map);
    
    infowindow = new google.maps.InfoWindow();
    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch({
        location: trespassos,
        radius: 500,
        type: ['store']
    }, callback);
}

function callback(results, status) {
    console.log(results);
    if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            createMarker(results[i]);
        }
    }
}

function createMarker(place) {
    var placeLoc = place.geometry.location;
    var marker = new google.maps.Marker({
        map: map,
        position: placeLoc
    });
    var infoWindow = addInfoWindow(place.name)
    addListener(map, marker, infoWindow);
}

function addMarker(position, map, title) { 
    return new google.maps.Marker({
        position: position,
        map,
        title
    });
 }

 function addInfoWindow(content) {
     return new google.maps.InfoWindow({
         content
     });
 }

 function addListener(map, marker, infoWindow) {
     return marker.addListener(
         'click',
        function() {
            infoWindow.open(map, marker)
        });
 }