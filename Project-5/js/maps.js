var map;

var trespassos = {
    lat: -27.455982,
    lng: -53.93018
}

function initMap() {
    // Constructor creates a new map - only center and zoom are required.
    map = new google.maps.Map(document.getElementById('map'), {
        center: trespassos,
        zoom: 13
    });

    var marker = addMarker(trespassos, map, "Tres Passos");
    var infowindow = addInfoWindow(`${marker.getPosition()}`);
   
    addListener(map, marker, infowindow);

    var placeSearchAutoComplete = new google.maps.places.Autocomplete(
        document.getElementById('search-box')
    );
    placeSearchAutoComplete.bindTo('bounds', map);
    
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