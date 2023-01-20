# health-companion
#### Video Demo: [url]
#### Description:
an app collating and trivialising tools of various functions relating to health and fitness

#### User guide:
When constructing a meal plan, enter on the main page the target calorie count, the percentage of daily calorie limit to be reserved for fats, and desired daily protein intake. Submit the form and the full macronutrient profile will be calculated.

Macronutrient energy density
Protein: 4kcal/g
Fat: 9kcal/g
Carbohydrate: 4kcal/g 

#### Files:

##### app.py
Contains basic components for a Flask app file such as imports and declaration of a Flask object.

The default '/' route has two methods. A user visiting the site for the first time will send a GET request, to which the site responds by simply rendering 'index.html'. After the user submits the form on 'index.html' via POST, the app will gather the information submitted in the form and fill a dictionary with key value pairs to be returned with the 'render_template' call to fill the table. If the user submits invalid input such as negative values or values that result in an impossible calculation e.g. 100% fat percentage and non-zero protein mass, an error message is built and returned with the render call.

Contains functions for database integration taken from flask documentation.

##### index.html
A barebones HTML file with a form consisting of input fields allowing the user to submit information about their desired meal plan, as well as tables (daily and weekly values) which, using jinja syntax, is either empty in the absence of the info dictionary, or filled with values calculated to fit with the user-defined constraints. div element at the top of main is populated with a dismissable alert if there is an error message to display.

##### foodData.db
A file to house all the data about the user's meal plan details and the custom foods involved. Contains table 'plan' which stores all the macronutrient profiles of any plans stored by the user, and table 'food' to which custom food items can be added with their nutritional details and other info such as price, price per kg, price per unit protein, link to an online retailer etc. Also contains another table which links these aforementioned two, so the foods to be included in each meal plan can be tracked.

##### schema.sql
A file describing the structure of foodData.db.