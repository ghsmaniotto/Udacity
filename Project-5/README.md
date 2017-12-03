# Project 5 - Neigborhood Map

## Description
A single page application featuring a map of your neighborhood or a neighborhood that you would like to visit. Add some functionality to this map including highlighted locations, third-party data about those locations and various ways to browse the content.

---

## Execution
The main file of the application is `index.html`. To display this project, you need to run this file in a browser.

When you open `index.html` in a browser, you will see a `map`, a `bar` in the top and a `button` in the bar. This button named `Places List` hide/show the `sidebar` that contains a `list of the places` and a `filter field` to filter the places by name.
A standard city is displayed with 20 markers about stores in that location.

### Click in marker
When some `marker` is `clicked` a info window is open, showing the name of the store/place.

### Filter 
To filter the places, you need to type the `place's name` at the text input and click and `filter button`.

### Click in list place
When some `list item` is `clicked` a info window is open in the marker, showing some `Foursquare's` statistics.

---

## Change the mail location

The default location is defined in the `app.js` file. Actually the default location is `Três Passos, Rio Grande do Sul, Brazil`.

To change this value, you need to change the `lat,lng` defined in the `defaultLocation` object.

</br>
</br>

---

PS: To create the sidebar I follow some instructions of this excelent tutorial: `https://bootstrapious.com/p/bootstrap-sidebar`

