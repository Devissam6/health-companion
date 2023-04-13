# health-companion
#### Video Demo: [https://youtu.be/DLbRi3ce2Yc]
#### Description:
an app collating and trivialising tools of various functions relating to health and fitness

## Files:

### app.py
From the flask module we need Flask for the app, redirect for navigating to another route, render_template for displaying templates and passing information to them, request for retrieving information from user-filled forms, and session for temporarily storing data for use across page requests.

Sqlite3 is used for facilitating all interactions with the database. Time is used to logging when a plan or custom food is added to the database. Configparser is used for getting the secret key, necessary to enable session data, from a separate config file. The security in hiding the secret key is not needed currently for the application but when scaled in the future may be required.

The get_db function connects to a SQLite database specified by the constant 'DATABASE', executes the SQL query string passed to it using the cursor, fetches all the results and stores it in the 'res' variable. It then commits the transaction and closes the database connection. The function then returns either the first row of the query result or the entire query result based on the 'one' parameter.

Every rendering of the template 'plan.html' requires fetching a list of all plans and all foods from the database, so functions get_plans and get_foods are used to condense the code.

Early versions of the app had functionality for the base route / but now is used just to redirect the user to the main route of the app, and to prevent 404 errors from loading non-existent pages.

The /plan route has two purposes: if the request method is POST, the user has begun the process of creating a new plan by filling in the fields for 'Target Calories', 'Protein Mass', and 'Fat Percentage', and submitting via the 'Preview' button. The app extracts them into the 'info' dictionary and performs checks for invalid inputs (if values are negative, protein mass greater than the calorie limit allows, or fat percentage greater than calorie limit and protein mass allows). Then more key value pairs are added to the dictionary, as calculated from the first three values, to fill in the daily and weekly macronutrient tables on 'plan.html', which happens when the complete dictionary is passed as an argument with the render call for 'plan.html'.

If the request method is GET, this route acts as a home page for the plan.html template. There are two outcomes depending on whether plan_id is stored in the session dictionary. Either will result in the app checking for a message stored in session data for displaying to the user. If there is a message, it is copied out of session data before being popped to reset it for messages created in future requests. The message can then be passed as an argument when rendering the template. If plan_id is in session data, it is as a result of the user loading an existing plan. In this case, the app retrieves data from the database about which foods have been added to the plan from the table plan_food_link to display at the bottom of plan.html, alongside the foods' nutrional information. The macronutrient distribution of the plan is also retrieved from the database to display in the tables above, for the user to review. If plan_id is not in session data, the user has not selected a plan to load and the food section at the bottom is not required.

The /saveplan route is requested when the user has inputted the plan constraints, previewed the macronutrient profile and then given the plan a name. This route is not intended to be accessed with GET requests, so the user is simply redirected back to /plan when doing so. If the request method is POST, all the daily values are retrieved from the request and stored in the info dictionary. After checking for invalid inputs in the fields for plan name and values, the data is stored into the plans table of the database. A message is stored in session, and the user is redirected back to /plan.

The /loadplan route also sends the user back to /plan is the request method is GET. In response to a POST request, the app retrieves the id number of the plan and takes one of two actions depending on the user's input from the radio buttons. If the user selects the load option, the id of the plan selected is stored in session data so in every future request for /plan, the app can get the currently loaded plan. If the user selects the delete option, the plan selected is removed from the database, alongside all the foods that were linked with that plan. The plan id stored in session data is removed to avoid errors. In both cases, a message confirming the action is stored in session data and the user is redirected to /plan.

The /food route acts as the home site of the food.html template. The database is queried for a list of all foods to display in the template. Then, as in /plan, any messages stored in session are copied out and passed on for the template when rendered.

The /savefood route is requested when the user submits the form on food.html. The app records the time the request was made to be stored in the database which is currently unused. The protein, mass, and price values are first stored in variables since they are needed to calculate values not directly inputted by the user, such as price per kg. All values are stored in a new entry in the foods table. A message is stored in session and the user is redirected back to /food.

The route /deletefood is requested when the user clicks the bin icon on one of the entries in the table on food.html. The button is part of a form with a hidden input containing the id of the food item, which is passed on when the button is pressed to allow the app to know which entry to delete.

The route /addfoodtoplan is requested when the user submits the form with the select input populated by foods to add to the plan. The app takes the input to filter instances where the user submits with the default (Select Food) option. Then the app adds an entry into the plan_food_link matching the plan id with the food id, setting the mass to a default value of 0.

The route /removefoodfromplan is requested when the user clicks the bin icon next to the food entry on plan.html. The app gets the food id from the hidden input from the button's form, and removes the corresponding entry from plan_food_link.

The route /updatefoodmass is requested when the user inputs a new mass for a food included in the plan and submits with the edit icon button. The app retrieves the mass and food id and updates the entry in the plan_food_link table.

### layout.html
Contains the constant structure of an HTML file that is needed for all pages, cutting down on redundant lines and streamlining modifications. Head contains integration for Bootstrap as CSS framework, Popper for tooltips support, and Fontawesome as an icon pack.

The body contains a responsive navbar with an icon, and links to all pages of the app. The script at the end of body initialises tooltips on the page (taken from Bootstrap v5.0 documentation). Within main there is a div dedicated to showing dismissable messages, for giving visual feedback to the user about errors or successful actions. The contents of the messages themselves are handled within the app.py file and passed on when rendering the template. Below that is the jinja block where the contents of each individual page are inserted.

### plan.html
A barebones HTML file with a form consisting of input fields allowing the user to submit information about their desired meal plan, as well as tables (daily and weekly values) which, using jinja syntax, is either empty in the absence of the info dictionary, or filled with values calculated to fit with the user-defined constraints. div element at the top of main is populated with a dismissable alert if there is an error message to display.

This page allows users to make modifications regarding meal plans. This includes creating and saving a plan, adding foods to that plan, and loading and deleting plans. These functions are achieved through the use of multiple forms throughout the page, which will be explained in order of user interaction.

The form submitting to route "/plan" contains a row of three inputs labelled "Target Calories", "Protein Mass", and "Fat Percentage". Once the user submits the form with this information by interacting with the button labelled "Preview", the inputted information is retrieved by the app which calculates the values to pass back to the template, where the user is shown the values filled in the two tables below, one for daily and the other for weekly energy distribution.

These two tables are part of the form submitting to route "/saveplan", which the user can use to save the energy profile into the database. The tables are nested in this form so that the values in the inputs can be retrieved by the app when submitted. There is another input below with a button that is used to enter a name for the plan to be saved.

The form at the top of the page, submitting to route "/loadplan", can be used to load existing plans or delete them. The select input displays an updated list of all plans saved in the database, which are provided by the app each time the page is refreshed or navigated to. The radio type buttons below allow the user to choose the action taken for the selected plan.

When the user selects a plan to load, the app uses the session dictionary to store the id of the plan so that the user doesn't need to select it again every time the page is refreshed or some other action is taken. With a plan loaded, a hidden section at the bottom of the page is revealed, which is used to add the user's custom foods to the plan.

Within this section, there is a form submitting to "/addfoodtoplan" which includes a select input populated with the current list of foods stored in the database, allowing the user to choose a selection of foods to fit the plan. Below is the table of foods currently included in the plan, as well as controls for each row in the list: a form, submitting to route "/updatefoodmass", with an input and button to edit the desired mass of that particular food included in the plan, as well as a delete button in a form submitting to route "/removefoodfromplan" to remove the food.

### food.html

This page is dedicated to managing existing custom food entries as well as adding new ones.

The top of the page has a form submitting to route "/savefood", containing fields for the user to input information about the food such as name, nutritional values, and also optional information like a link to it's page on an online retailer and notes about the particular food.

Below is a table displaying all the custom food entries in the database. Each row has a form, submitting to route "/deletefood", with a button that allows the user to remove a food from the database.

### foodData.db
A file to house all the data about the user's meal plan details and the custom foods involved.

### schema.sql
Contains commands describing the structure of the database used by the app to store information about the user's nutrition plan.

The 'plans' table stores information about the user's meal plans. It has fields for the plan's name, date created, the mass and energy specification of all three macronutrients, as well as the total energy.

The 'foods' table stores information about the user's custom foods. It has fields for the food's name, date added, food type, its nutritional values per 100g, its mass and the price at which it can be bought, as well as calculated price per kg and per 20g of protein provided. The link and notes fields are optional and can be filled by the user to provide extra functional benefit in the app.

The 'plan_food_link' table stores information about how much of a particular food is included in a plan. There are fields for the plan id, the food id, and the mass of that food included.

### init_db.py
This is used to initialise an empty new database file with the required table structure to be used with the app.

A first time user must create an empty .db file and run init.db.py, passing it as an argument to correctly initialise the database.

The file has checks in place to ensure proper usage, then uses commands from the sqlite3 library to open the .db file and execute the commands within the schema.sql file.