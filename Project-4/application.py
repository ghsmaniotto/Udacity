# Import the framework Flask methods
from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify, g, make_response
# SQLAlchemy to manage the database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import asc, exc
from catalog_db import User, Base, CatalogCategory, CategoryItem
# HTTPBasichAuth to improve the security in the application
from flask_httpauth import HTTPBasicAuth
from flask import session as login_session
import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

auth = HTTPBasicAuth()
catalog_app = Flask(__name__)

# Create a sqlalchemy session to manage the database
engine = create_engine("{}".format("sqlite:///catalog_app.db"))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

"""	Load the google API info's to create a
third-party authentication and authorization"""
CLIENT_ID = json.loads(
    open("client_secrets_google.json", "r").read())["web"]["client_id"]
# Set the application name
APPLICATION_NAME = "Catalog Item Application"


@catalog_app.route("/")
@catalog_app.route("/index")
@catalog_app.route("/catalog")
def showAllCatalog():
    """	This is the Application's homepage.
    It shows the categories and 10 recently added items.
    It makes calls to DB to get the necessary information."""

    # If the user is logged is render the private page
    # and the public one otherwise
    if "username" not in login_session:
        try:
            catalog_categories = session.query(
                CatalogCategory).order_by(
                asc(CatalogCategory.name)).all()
            items = session.query(
                CategoryItem).order_by(
                CategoryItem.id).limit(
                10).all()
        except (exc.SQLAlchemyError, exc.DBAPIError):
            session.rollback()
            flash("""Occurred an error in our server.
                Please, try again in a few minutes!""")
        return render_template(
            "public_catalog.html",
            catalog_categories=catalog_categories,
            items=items)
    else:
        try:
            catalog_categories = session.query(
                CatalogCategory).order_by(
                asc(CatalogCategory.name)).all()
            items = session.query(
                CategoryItem).order_by(
                CategoryItem.id).limit(
                10).all()
        except (exc.SQLAlchemyError, exc.DBAPIError):
            session.rollback()
            flash("""Occurred an error in our server.
                Please, try again in a few minutes!""")
        return render_template(
            "private_catalog.html",
            catalog_categories=catalog_categories,
            items=items)


@catalog_app.route("/login")
def showLogin():
    """
    This method renders the login page to the user.
    This page contains two third-party authentication and authorization.
    The Google and Facebook ones.
    """
    """Create a state variable within the user to guarantee that
    it is the real user who does the login.
    This variable is a token that is sent to
    third-party server to create a token-session."""
    state = "".join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)


@catalog_app.route("/catalog/<string:category>")
@catalog_app.route("/catalog/<string:category>/items")
def showCategoryItems(category):
    """The function that is called to response the category request.
    Input: a string representing the category's name.
        - <string:category>
    Returns:
        - A public page that the user is able to read the category items,
            only.
        - A private page that the user is able to edit and delete the category
            and add new items if the user is logged in and
            he is the category's creator.
    """
    try:
        # Get the catalog category from database
        category_db = session.query(
            CatalogCategory).filter_by(
            name=category).one()
        # Get the category items from database
        items = session.query(
            CategoryItem).join(
            CatalogCategory).filter(
            CatalogCategory.name == category).order_by(
            CategoryItem.name)
    except (exc.SQLAlchemyError, exc.DBAPIError):
        # Rollback the current transaction in progress.
        session.rollback()
        flash("""Occurred an error in our server.
            Please, try again in a few minutes!""")
        flash("Maybe the selected category does not exist!")
        # Redirect to the homepage
        return redirect(url_for("showAllCatalog"))
    try:
        # Get the category creator user
        creator = session.query(User).filter_by(id=category_db.user_id).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        # Rollback the current transaction in progress.
        session.rollback()
        flash("""Occurred an error in our server.
            Please, try again in a few minutes!""")
        flash("Maybe your user does not exist!")
        # Redirect to the homepage
        return redirect(url_for("showAllCatalog"))

    # If the user is not logged or is not the creator render the public page
    if ("username" not in login_session or
            creator.id != login_session["user_id"]):
        return render_template(
            "public_category_items.html",
            category=category,
            items=items,
            items_number=items.count())
    else:
        # If the user is not logged or is not the
        # creator render the private page
        return render_template(
            "private_category_items.html",
            category=category,
            items=items,
            items_number=items.count())


@catalog_app.route("/catalog/<string:category>/<string:item>")
def showCategoryItem(category, item):
    """The function that is called to response the item request.
    Input: a string representing the category's name and the item's name.
        - <string:category> and <string:item
    Returns:
        - A public page that the user is able to read the item description,
            only.
        - A private page that the user is able to edit and delete the item
            if the user is logged in and is the category's creator.
    """
    try:
        # Get the item from the database
        item_catalog = session.query(
            CategoryItem).join(
            CatalogCategory).filter(
            CatalogCategory.name == category).filter(
            CategoryItem.name == item).one()
        # Get the item creator user
        creator = session.query(
            User).filter_by(
            id=item_catalog.user_id).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        flash("""Occurred an error in our server.
            Please, try again in a few minutes!""")
        flash("Maybe the item does not exist!")
        # Rollback the current transaction in progress.
        session.rollback()
        return render_template(url_for("showAllCatalog"))

    # If the user is logged the private page is rendered,
    # the public one otherwise
    if ("username" not in login_session or
            creator.id != login_session["user_id"]):
        return render_template(
            "public_items_description.html",
            item=item_catalog)
    else:
        return render_template(
            "private_items_description.html",
            item=item_catalog)


@catalog_app.route("/catalog/category/new", methods=["GET", "POST"])
def newCategory():
    """The function that is called to response the create new category request.
    It creates a new category named with the name form input.
    The logged in user is the creator of the category and he is the unique that
        is able to edit and delete them.
    """
    # Get the user from the login session
    if "username" not in login_session:
        return redirect("/login")
    # If is a GET request and the user is logged in,
    # a form to create new category is returned
    if request.method == "GET":
        return render_template("new_category.html")
    # If is a POST request, try to add the new category to the database
    elif request.method == "POST":
        # Try to insert new category to the database
        try:
            newCategory = CatalogCategory(
                name=request.form["name"],
                user_id=login_session["user_id"])
            session.add(newCategory)
            session.commit()
        except (exc.SQLAlchemyError, exc.DBAPIError):
            flash("Was not possible to create a new category")
            flash("Maybe this category exists already!")
            # Rollback the insert method in progress.
            session.rollback()
            # Rendering the new category again
            return render_template("new_category.html")

    flash("New Category {} Successfully Created".format(newCategory.name))
    # Returns the new category items page
    return redirect(url_for("showCategoryItems", category=newCategory.name))


@catalog_app.route(
    "/catalog/<string:category>/delete",
    methods=["GET", "POST"])
def deleteCategory(category):
    """The function that is called to response the delete a category request.
    It delete a category named with the form name input.
    Only the the creator and logged user is able to delete the category.
    """
    # Get the user from the login session
    if "username" not in login_session:
        return redirect("/login")
    # Get the category data from database
    try:
        categoryToDelete = session.query(
            CatalogCategory).filter_by(
            name=category).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        flash("""Occurred an error in our server.
        Please, try again in a few minutes!""")
        flash("Maybe the category does not exist yet!")
        session.rollback()
        # Render the delete category page again
        return render_template(
            "delete_category.html",
            category=categoryToDelete)

    # To delete category the user must be the creator
    if categoryToDelete.user_id != login_session["user_id"]:
        return """<script>function myFunction() {alert(
            "You are not authorized to delete this category.
            Please create your own category in order to delete."
            );} </script><body onload="myFunction()"">"""
    # If is a POST request, try to delete the category
    if request.method == "POST":
        session.delete(categoryToDelete)
        flash("{} Successfully Deleted".format(categoryToDelete.name))
        session.commit()
        return redirect(url_for("showAllCatalog"))
    # If is a GET request, redirect the user to delete category page
    else:
        return render_template(
            "delete_category.html",
            category=categoryToDelete)


@catalog_app.route("/catalog/<string:category>/edit", methods=["GET", "POST"])
def editCategory(category):
    """The function that is called to response the edit a category request.
    It edit a selected category from its page
    Only the the creator and logged user is able to edit the category.
    """
    # Get the user from the login session
    if "username" not in login_session:
        return redirect("/login")
    try:
        editedCategory = session.query(
            CatalogCategory).filter_by(
            name=category).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        flash("""Occurred an error in our server.
            Please, try again in a few minutes!""")
        flash("Maybe the category does not exists!")
        session.rollback()
        # Redirect to the category page
        return redirect(url_for("showCategoryItems", category=category))

    # To edit category the user must be the creator
    if editedCategory.user_id != login_session["user_id"]:
        return """<script>function myFunction() {alert(
            "You are not authorized to edit this category.
            Please create your own category in order to edit."
            );} </script><body onload="myFunction()"">"""
    # If it is an POST request, try to edit the category info's
    if request.method == "POST":
        # If there is data in form, change the category name
        if request.form["name"]:
            # Try to edit the category in the database
            try:
                editedCategory.name = request.form["name"]
                session.add(editedCategory)
                session.commit()
                flash("Category {} Successfully Edited".format(
                    editedCategory.name))
                return redirect(url_for(
                    "showCategoryItems",
                    category=editedCategory.name))
            except (exc.SQLAlchemyError, exc.DBAPIError):
                flash("Category {} Wasn\'t Edited".format(
                    editedCategory.name))
                flash("Maybe the edited category already exists!")
                # Rollback the current session method
                session.rollback()
                return redirect(url_for(
                    "showCategoryItems",
                    category=category))
    else:
        # If it is a GET request, returns the edit category form page
        return render_template("edit_category.html", category=editedCategory)


@catalog_app.route(
    "/catalog/<string:category>/item/new",
    methods=["GET", "POST"])
def newItem(category):
    """
    The function that is called to response the create new item request.
    It creates a new item named with the name form input.
    The logged in user is the creator of the item and he is the unique that
        is able to edit and delete them.
    """
    # Get the user from the login session
    if "username" not in login_session:
        return redirect("/login")
    try:
        # Get the category from the database
        category_db = session.query(
            CatalogCategory).filter_by(
            name=category).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        # If is not possible query the database, rollback the current action
        session.rollback()
        flash("The category is not defined!")
        # Redirect to the home page
        return redirect(url_for("showAllCatalog"))

    # If is a GET request and the user is logged in,
    # a form to create new item is returned
    if request.method == "GET":
        return render_template("new_item.html", category=category_db)
    # If is a POST request, try to add the new item to the database
    elif request.method == "POST":
        # Try to insert new item to the database
        try:
            newItem = CategoryItem(
                name=request.form["name"],
                description=request.form["description"],
                catalog_category_id=category_db.id,
                user_id=login_session["user_id"])
            session.add(newItem)
            session.commit()
        except (exc.SQLAlchemyError, exc.DBAPIError):
            # Rollback the insert method in progress.
            session.rollback()
            flash("""The item: {} exists already,
                you can added in this category""".format(newItem.name))
            # Rendering the new item form again
            return render_template("new_item.html", category=category_db)

    flash("New Item {} to Category {} successfully created".format(
        newItem.name,
        category_db.name))
    # Redirect to the new item description page
    return redirect(url_for(
        "showCategoryItem",
        category=category_db.name,
        item=newItem.name))


@catalog_app.route(
    "/catalog/<string:category>/<string:item>/delete",
    methods=["GET", "POST"])
def deleteItem(category, item):
    """
    The function that is called to response the delete a item request.
    It delete an item identified by the category and item names
    Only the the creator and logged user is able to delete the item.
    """
    # Get the user from the login session
    if "username" not in login_session:
        return redirect("/login")
    # Get the item data from database
    try:
        itemToDelete = session.query(
            CategoryItem).join(
            CatalogCategory).filter(
            CatalogCategory.name == category).filter(
            CategoryItem.name == item).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        session.rollback()
        flash("This item does not exists in this category!")
        # Render the category items page
        return redirect(url_for("showCategoryItems", category=category))

    # To delete category the user must be the creator
    if itemToDelete.user_id != login_session["user_id"]:
        return """<script>function myFunction() {alert(
            "You are not authorized to delete this item.
            Please create your own item in order to delete."
            );} </script><body onload="myFunction()"">"""
    # If is a POST request, try to delete the item
    if request.method == "POST":
        try:
            session.delete(itemToDelete)
            session.commit()
        except (exc.SQLAlchemyError, exc.DBAPIError):
            session.rollback()
            flash("Was not possible to delete this item!")
            flash("Maybe the item does not exist in this category yet!")
            return redirect(url_for("showCategoryItems", category=category))

        flash("Item Successfully Deleted")
        return redirect(url_for("showCategoryItems", category=category))
    else:
        # If is a GET request, redirect the user to delete item page
        return render_template("delete_item.html", item=itemToDelete)


@catalog_app.route(
    "/catalog/<string:category>/<string:item>/edit",
    methods=["GET", "POST"])
def editItem(category, item):
    """
    The function that is called to response the edit an edit request.
    It edit a selected item from its page description.
    Only the the creator and logged user is able to edit the item.
    """
    # Get the user from the login session
    if "username" not in login_session:
        return redirect("/login")
    try:
        editedItem = session.query(
            CategoryItem).join(
            CatalogCategory).filter(
            CatalogCategory.name == category).filter(
            CategoryItem.name == item).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        flash("""Occurred an error in our server.
        Please, try again in a few minutes!""")
        session.rollback()
        print("Error to edit item!")
        # Redirect to the category page
        return redirect(url_for("showCategoryItems", category=category))

    # To edit the item the user must be the creator
    if editedItem.user_id != login_session["user_id"]:
        return """<script>function myFunction() {alert(
            "You are not authorized to edit this item.
            Please create your own item in order to edit."
            );} </script><body onload="myFunction()"">"""

    # If it is an POST request, try to edit the item info's
    if request.method == "POST":
        # If there is data in form, change the item name
        if request.form["name"]:
            editedItem.name = request.form["name"]
        # If there is data in form, change the item description
        if request.form["description"]:
            editedItem.description = request.form["description"]
        # Try to edit the item in the database
        try:
            session.add(editedItem)
            session.commit()
        except (exc.SQLAlchemyError, exc.DBAPIError):
            flash("Was not possible to edit this item!")
            flash("Maybe the item exists already!")
            # Rollback the current session method
            session.rollback()
            return redirect(url_for("showCategoryItems", category=category))

        flash("Category Item Successfully Edited")
        return redirect(url_for(
            "showCategoryItems",
            category=editedItem.catalog_category.name))
    else:
        # If it is a GET request, returns the edit item form page
        return render_template("edit_item.html", item=editedItem)


@catalog_app.route("/catalog/catalog.json", methods=["GET"])
def jsonCatalog():
    """
    The function that returns a JSON format output that contains
    all database data. Including all categories and all items.
    """
    output = {}
    # Get all the categories from the database
    categories = session.query(CatalogCategory).all()
    for category in categories:
        # Get all items from the category
        items = session.query(
            CategoryItem).filter_by(
            catalog_category=category).all()
        # Add this values to the output dictionary
        output[category.name] = [item.serialize for item in items]
    # Creates a JSON format output
    return jsonify(CatalogCategories=output)


@catalog_app.route(
    "/catalog/<string:category>/category.json",
    methods=["GET"])
def jsonCategory(category):
    """
    The function that returns a JSON format output that contains
    all items of a category.
    """
    try:
        category_db = session.query(
            CatalogCategory).filter_by(
            name=category).one()
        items = session.query(
            CategoryItem).filter_by(
            catalog_category=category_db).all()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        flash("The required category does not exist.")
        flash("Sorry, try another category or create a new one.")
        return url_for('showAllCatalog')
    # Create a JSON format of category items
    return jsonify(Category=[item.serialize for item in items])


@catalog_app.route(
    "/catalog/<string:category>/<string:item>/item.json",
    methods=["GET"])
def jsonItem(category, item):
    """
    The function that returns a JSON format output that contains
    all items of a category.
    """
    try:
        jsonItem = session.query(
            CategoryItem).join(
            CatalogCategory).filter(
            CatalogCategory.name == category).filter(
            CategoryItem.name == item).one()
    except (exc.SQLAlchemyError, exc.DBAPIError):
        flash("The required item does not exist.")
        flash("Sorry, try another item or create a new one.")
        return url_for('showAllCatalog')
    # Create a JSON format of category items
    return jsonify(Item=jsonItem.serialize)


@catalog_app.route("/gconnect", methods=["POST"])
def gconnect():
    # Validate state token
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            "client_secrets_google.json",
            scope="")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/\
        v1/tokeninfo?access_token={}".format(
        access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url.replace(" ", ""), "GET")[1])
    # If there was an error in the access token info, abort.
    if result.get("error") is not None:
        response = make_response(json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is valid for this app.
    if result["issued_to"] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers["Content-Type"] = "application/json"
        return response

    stored_access_token = login_session.get("access_token")
    stored_gplus_id = login_session.get("gplus_id")
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                "Current user is already connected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    # Store the access token in the session for later use.
    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    print("JSON resposta:")
    print(data)

    login_session["username"] = data["name"]
    login_session["picture"] = data["picture"]
    login_session["email"] = data["email"]
    # ADD PROVIDER TO LOGIN SESSION
    login_session["provider"] = "google"
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session["user_id"] = user_id

    output = ""
    output += "<h1>Welcome, "
    output += login_session["username"]
    output += "!</h1>"
    output += "<img src="
    output += login_session["picture"]
    output += " style = 'width: 300px; height: 300px;border-radius: 150px;\
        -webkit-border-radius: 150px;-moz-border-radius: 150px;'> "
    flash("you are now logged in as {}".format(login_session["username"]))
    print("done!")
    return output


@catalog_app.route("/gdisconnect", methods=["POST"])
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get("access_Token")
    if access_token is None:
        response = make_response(
            json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    url = "https://accounts.google.com/\
        o/oauth2/revoke?token={}".format(
            access_token)
    h = httplib2.Http()
    result = h.request(url, "GET")[0]
    if result["status"] == "200":
        response = make_response(json.dumps(
                                "Successfully disconnected."),
                                200)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        response = make_response(json.dumps(
                                "Failed to revoke token for given user.",
                                400))
        response.headers["Content-Type"] = "application/json"
        return response


@catalog_app.route("/fbconnect", methods=["POST"])
def fbconnect():
    access_token = request.data
    print "access token received {}!!".format(access_token)

    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    app_id = json.loads(open(
                        "client_secrets_fb.json",
                        "r").read())["web"]["app_id"]
    app_secret = json.loads(open(
                            "client_secrets_fb.json",
                            "r").read())["web"]["app_secret"]
    url = "https://graph.facebook.com/oauth/\
        access_token?grant_type=fb_exchange_token&\
        client_id={}&client_secret={}&fb_exchange_token={}".format(
                                                                app_id,
                                                                app_secret,
                                                                access_token)

    h = httplib2.Http()
    result = h.request(url.replace(" ", ""), "GET")[1]

    # Due to the formatting for the result from
    # the server token exchange we have to
    # split the token first on commas and
    # select the first index which gives us the key : value
    # for the server access token then we split it on colons
    # to pull out the actual token value
    # and replace the remaining quotes with nothing so
    # that it can be used directly in the graph api calls
    # token = json.loads(result)
    token = result.split(",")[0].split(":")[1].replace('"', "")
    url = "https://graph.facebook.com/v2.10/me?\
        access_token={}&fields=name,id,email".format(token)
    h = httplib2.Http()
    result = h.request(url.replace(" ", ""), "GET")[1]
    data = json.loads(result)
    login_session["provider"] = "facebook"
    login_session["username"] = data["name"]
    login_session["email"] = data["email"]
    login_session["facebook_id"] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session["access_token"] = token

    login_session["picture"] = "https://graph.facebook.com/\
                                v2.10/{}/picture".format(
                                login_session["facebook_id"]).replace(" ", "")

    # see if user exists
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session["user_id"] = user_id

    output = ""
    output += "<h1>Welcome, "
    output += login_session["username"]

    output += "!</h1>"
    output += "<img src="
    output += login_session["picture"]
    output += "style = 'width: 300px; height: 300px;border-radius:\
        150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;'> "

    flash("Now logged in as {}".format(login_session["username"]))
    return output


# @catalog_app.route("/fbdisconnect", methods=["POST"])
def fbdisconnect():
    facebook_id = login_session["facebook_id"]
    # The access token must me included to successfully logout
    access_token = login_session["access_token"]
    url = "https://graph.facebook.com/{}/\
        permissions?access_token={}".format(
                                            facebook_id,
                                            access_token)
    h = httplib2.Http()
    result = h.request(url, "DELETE")[1]
    return "you have been logged out"


# Disconnect based on provider
@catalog_app.route("/disconnect")
def disconnect():
    if "provider" in login_session:
        if login_session["provider"] == "google":
            gdisconnect()
            del login_session["gplus_id"]
            # del login_session["credentials"]
        if login_session["provider"] == "facebook":
            fbdisconnect()
            del login_session["facebook_id"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]
        del login_session["provider"]
        del login_session["access_token"]
        flash("You have successfully been logged out.")
        return redirect(url_for("showAllCatalog"))
    else:
        flash("You were not logged in")
        return redirect(url_for("showAllCatalog"))


def getUserID(user_email):
    """Get user id from the database using the email info"""
    try:
        user = session.query(User).filter_by(email=user_email).one()
        return user.id
    except:
        return None


def getUserInfo(user_ID):
    """Get the user info from the database using the user ID"""
    try:
        user = session.query(User).filter_by(id=user_ID).one()
        return user
    except:
        return None


def createNewUser(login_session):
    """This method add new users to the database"""
    # Creates the new user with the session info
    newUser = User(
        name=login_session["username"],
        email=login_session["email"],
        picture=login_session["picture"])
    # Add the new user to the database
    session.add(newUser)
    session.commit()
    # Get the user data from the database using the email info
    user = session.query(User).filter_by(email=login_session["email"]).one()
    # Returns the user id
    return user.id


if __name__ == "__main__":
    catalog_app.secret_key = "super-secret-key"
    catalog_app.debug = True
    catalog_app.run(host="0.0.0.0", port=8000)
