// MAP DATA
var map;
var infowindow;
var markersList = [];
var viewModel = new PlaceListViewModel(map);

var trespassos = {
    lat: -27.455982,
    lng: -53.93018
};
// MAP - CONTENT

function initMap() {
    // Constructor creates a new map - only center and zoom are required.
    map = new google.maps.Map(document.getElementById('map'), {
        center: trespassos,
        zoom: 16
    });
    infowindow = new google.maps.InfoWindow();

    // var placeSearchAutoComplete = new google.maps.places.Autocomplete(
    //     document.getElementById('search-box')
    // );
    
    // placeSearchAutoComplete.bindTo('bounds', map);

    var service = new google.maps.places.PlacesService(map);
    service.nearbySearch({
        location: trespassos,
        radius: 500,
        type: ['store']
    }, callback);
};

function callback(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            markersList.push(createMarker(results[i]));
        }
    }
};

function createMarker(place) {
    var placeLoc = place.geometry.location;
    var marker = new google.maps.Marker({
        map: map,
        position: placeLoc,
        title: place.name
    });
    // var infoWindow = addInfoWindow(place.name)
    addListener(map, marker, infowindow);
    viewModel.addPlace(marker);
    return marker;
};

function addMarker(position, map, title) {
    return new google.maps.Marker({
        position: position,
        map,
        title
    });
};

function addInfoWindow(content) {
    return new google.maps.InfoWindow({
        content
    });
};

function addListener(map, marker, infowindow) {
    return marker.addListener(
        'click',
        function () {
            infowindow.setContent(marker.title);
            infowindow.open(map, marker);
        });
};

/* 
    Knockout JS
                */

function Place(marker) {
    this.marker = ko.observable(marker);
};

function PlaceListViewModel(map) {
    // Data
    var self = this;
    self.map = ko.observable(map);
    self.places = ko.observableArray();
    self.filter = ko.observable();
    self.placesList = ko.observableArray();

    // self.incompleteTasks = ko.computed(function () {
    //     return ko.utils.arrayFilter(self.tasks(), function (task) { return !task.isDone() });
    // });

    // Operations
    self.addPlace = function (marker) {
        self.places.push(new Place(marker));
    };

    self.showInfoWindow = function(place){ 
        infowindow.setContent(place.marker().title);
        infowindow.open(self.map, place.marker());
    };

    self.filteredItems = ko.computed(function () {
        var filter = self.filter();
        if (!filter) {
            return self.places();
        } else {
            return ko.utils.arrayFilter(self.places(), function (place) {
                return place.marker().title.includes(filter);
            });
        }
    });
};

ko.applyBindings(viewModel);
