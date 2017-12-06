# Catalog Application

It is a web application that provides a list of items within a variety of categories as well as provides a user registration and authentication system.

## **Project technologies**
It is a **Python** and **Flask Framework** based application.
The **SQLAlchemy** is the ORM (Object Relational Mapper) adopted by the project.
As the database is used the **SQLite** database.
The **Bootstrap Framework** (using **CSS**, **HTML** and **JavaScript**) is used to design the front-end application.
The **Facebook** and **Google** login are the unique way to create a user account and login in the application.

## **Application Features**
- All users are able to navigate and search the categories and items descriptions in the application. There are two lists in the home page, one of categories and another of items and the user can navigates over this content.
- However, only logged users are able to create, edit and delete categories and items. Privated pages are provided to users apply this changes.
- All users are able to get the informations from the application in JSON format.

## **How to use**
##### Populate the database
To start the application with some data stored in the database you can type in the terminal:
```sh
$ python lotofitems.py
```
This python script will create some categories and items into the database.

##### Start the application
The application.py file is the main file and to run the applications you need type in terminal
```sh
$ python application.py
```
Using this script, the application will listen in 8000 port. By the way, it is necessary to go to http://localhost:8000 address to access the application.

##### Cancel the application
To cancel the application you can press
```sh
ctrl + c
```

#### Accessing the application content
##### Edit, create and delete
To create, edit and delete an item or a category it is necessary to be logged in. To do it, it is necessary to click in login buttons in the home page. 
The user can loggin in the application only by Facebook and Google accounts.

##### Home page
The application main page can be accessed by the urls:
```sh
localhost:8000
localhost:8000/catalog
localhost:8000/index
```
##### Specific category
To access the categories items in JSON format it is necessary to type:
```sh
localhost:8000/catalog/<category_name>
localhost:8000/catalog/<category_name>/items
```
where <category_name> need to be replaced by the wanted category.
##### Specific item
To access the item description it is necessary to type:
```sh
localhost:8000/catalog/<category_name>/<item_name>
```
where <category_name> and <item_name> need to be replaced by the wanted category and item, respectively.
##### All JSON content
To get all application content in JSON format, you need to type 
```sh
localhost:8000/catalog/catalog.json
```
##### JSON category
To access the categories items in JSON format it is necessary to type:
```sh
localhost:8000/catalog/<category_name>/category.json
```
where <category_name> need to be replaced by the wanted category.
##### JSON item
To access the item description in JSON format it is necessary to type:
```sh
localhost:8000/catalog/<category_name>/<item_name>/item.json
```
where <category_name> and <item_name> need to be replaced by the wanted category and item, respectively.

## **Project details**
The project is divided as follow:

  - In the main project folder:
    - application.py: the backend application, developed using flask framework.
    - catalog_db.py: the database description.
    - client_secrets_fb.json: the third-party facebook API (app id, app secret)
    - client_secrets_google.json: the third-party google API (app id, app secret, auth_uri, others)
    - lotofitems.py: python script to add content into database.
    - static folder: folder that there are js and css files.
    - templates folder: folder that there are all html pages.
  - static folder:
    - css:
      - bootstrap.min.css: the bootstrap css file.
      - bootstrap.min.css.map: css maps.
      - starter-template.css: the personal css style.
    - js:
      - bootstrap.min.js: the bootstrap java script file.
      - popper.min.js: the pooper and tooltips placer. 
  - templates folder:
       - delete_category.html: html file to confirm the delete category action.
       - delete_item.html: html file to confirm the delete item action.
       - edit_category.html: html file that provide a form to edit a category.
       - edit_item.html: html file that provide a form to edit an item.
       - header.html: template for a html header for all application pages.
       - login.html: html file that provide a Facebook and Google third-party loggin.
       - main.html: template for all html applications pages.
       - new_category.html: html file with a form to create a new category.
       - new_item.html: html file with a form to create a new item.
       - private_catalog.html: html file to show all catalog to logged user.
       - private_category_items.html: html file to show all category items to logged user.
       - private_items_description.html: html file to show the item description to logged user.
       - public_catalog.html: html file to show all catalog to non logged user.
       - public_category_items.html: html file to show all category items to non logged user.
       - public_items_description.html: html file to show the item description to non logged user.
