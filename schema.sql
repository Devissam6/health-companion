-- SQLite
CREATE TABLE plan (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    plan_name TEXT NOT NULL,
    date_created DATETIME NOT NULL,
    protein_energy NUMERIC NOT NULL,
    protein_mass NUMERIC NOT NULL,
    fat_energy NUMERIC NOT NULL,
    fat_mass NUMERIC NOT NULL,
    carbohydrate_energy NUMERIC NOT NULL,
    carbohydrate_mass NUMERIC NOT NULL);
CREATE TABLE food (
    food_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    food_name TEXT NOT NULL,
    date_added DATETIME NOT NULL,
    type TEXT NOT NULL,
    energy NUMERIC NOT NULL,
    fat NUMERIC NOT NULL,
    saturated_fat NUMERIC NOT NULL,
    carbohydrates NUMERIC NOT NULL,
    sugar NUMERIC NOT NULL,
    fibre NUMERIC NOT NULL,
    protein NUMERIC NOT NULL,
    salt NUMERIC NOT NULL,
    mass NUMERIC NOT NULL,
    price NUMERIC NOT NULL,
    price_per_kg NUMERIC NOT NULL,
    price_per_20g_protein NUMERIC NOT NULL,
    link TEXT,
    notes TEXT);
CREATE TABLE plan_food_link (
    plan_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    FOREIGN KEY(plan_id) REFERENCES plan(plan_id),
    FOREIGN KEY(food_id) REFERENCES food(food_id));