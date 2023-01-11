# health-companion
## Changelog

#### Commit 1 (23/01/08)
1. Implement basic function of a macro calculator:
   - Has two input fields and a table, within which is another input field;
   - takes as input from user the target calorie count, percentage of calories as fat, and protein quantity;
   - '/' route calculates and populates rest of table with values according to macro energy densities.

##### Todo
- [x] (Completed 23/01/09) Data validation and 'misuse cleanup'
- [x] (Completed 23/01/09) Apply basic styling with Bootstrap
- [x] (Completed 23/01/09) Add table for weekly macro values
- [x] (Completed 23/01/09) Add styling for layout adjustment for different screen sizes

#### Commit 2 (23/01/11)
1. Start to integrate functionality to interact with a database:
   - 'foodData.db' contains all data. Structure described by 'schema.sql';
   - functions in 'app.py' taken from Flask documentation:
     - get_db opens connection to the database;
     - query_db executes SQL statements to allow communication between app and database;
     - init_db initialises tables in database with structure defined in a schema file;

##### Todo
- [ ] Define structure in schema and build database
      - Table storing meal plan constraints and macro details of user
      - Table storing custom foods with their nutritional information
- [ ] Build interface to interact with database from app
      - Must allow user to edit meal plan constraints
      - Must allow user to add and remove custom foods
