from flask import Flask, redirect, render_template, request, session
import sqlite3
import time
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('secrets.cfg')
app.secret_key = config["DEFAULT"]["SECRET_KEY"]
DATABASE = config["DEFAULT"]["DATABASE"]

# Simple function to query the database (adapted from Flask documentation)
def get_db(query, args=(), one=False):
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.row_factory = sqlite3.Row

    res = cur.execute(query, args).fetchall()
    db.commit()
    db.close()

    return (res[0] if res else None) if one else res

# Pull plan and food detail from database to be used in templates
def get_plans():
    return get_db("SELECT * FROM plans")

def get_foods():
    return get_db("SELECT * FROM foods")

@app.route("/", methods=["GET"])
def index():
    return redirect("/plan")

@app.route("/plan", methods=["GET", "POST"])
def plan():
    # Response to POST request (user submitted plan constraints by clicking "Preview" button)
    if request.method == "POST":
        # Gather info from form
        info = {"targetCal": request.form.get("targetCal", -1, float), 
                "proteinMass": request.form.get("proteinMass", -1, float),
                "fatPercent": request.form.get("fatPercent", -1, float)}
        # Return error for invalid input
        if (info["targetCal"] < 0 or
            (info["proteinMass"] < 0 or info["proteinMass"] > (1/4) * info["targetCal"]) or
            (info["fatPercent"] < 0 or ((info["fatPercent"]/100) * info["targetCal"] > info["targetCal"] - 4 * info["proteinMass"]) or info["fatPercent"] > 100)):
            session["errorMsg"] = "Constraints specified invalid. Please try again."
            return redirect("/plan")

        # Calculate values to fill table
        info["proteinEnergy"] = info["proteinMass"] * 4
        info["fatEnergy"] = info["targetCal"] * (info["fatPercent"]/100)
        info["fatMass"] = info["fatEnergy"] * (1/9)
        info["carbEnergy"] = info["targetCal"] - info["proteinEnergy"] - info["fatEnergy"]
        info["carbMass"] = info["carbEnergy"] * (1/4)
        info["totalEnergy"] = info["targetCal"]
        # Render index page with values in info, retrieved plans from database
        return render_template("plan.html", info=info, plansList=get_plans(), foodList=get_foods(), successMsg="Values calculated. Review and save to a plan below.")
    # Response to GET request
    else:
        # Retrieve all plans from database
        if "plan_id" not in session:
            if "errorMsg" in session:
                errorMsg = session["errorMsg"]
                session.pop("errorMsg")
                return render_template("plan.html", plansList=get_plans(), errorMsg=errorMsg)    
            elif "successMsg" in session:
                successMsg = session["successMsg"]
                session.pop("successMsg")
                return render_template("plan.html", plansList=get_plans(), successMsg=successMsg)    
            else:
                return render_template("plan.html", plansList=get_plans())
        else:
            res = get_db("SELECT * FROM plans WHERE plan_id = ?", (session["plan_id"]), one=True)

            info = {"planName": res["plan_name"],
                    "dateTimeCreated": res["date_created"],
                    "proteinEnergy": res["protein_energy"],
                    "proteinMass": res["protein_mass"],
                    "fatEnergy": res["fat_energy"],
                    "fatMass": res["fat_mass"],
                    "carbEnergy": res["carbohydrate_energy"],
                    "carbMass": res["carbohydrate_mass"],
                    "totalEnergy": res["total_energy"],
                    "targetCal": res["total_energy"],
                    "fatPercent": 100*res["fat_energy"]/res["total_energy"]}
            
            foodInfo = get_db("""SELECT f.food_id, f.food_name, f.energy, f.fat, f.saturated_fat, f.carbohydrates, f.sugar, f.fibre, f.protein, f.salt, f.price_per_kg, f.link, f.notes, pfl.mass
                            FROM foods AS f, plan_food_link AS pfl 
                            WHERE f.food_id = pfl.food_id AND pfl.plan_id = ?""", (session["plan_id"],))
            
            foodInfoTotal = {"energy": 0, "fat": 0, "saturated_fat": 0, "carbohydrates": 0, "sugar": 0, "fibre": 0, "protein": 0, "salt": 0, "price": 0, "mass": 0}
            for food in foodInfo:
                foodInfoTotal["energy"] += food["energy"] * food["mass"] / 100
                foodInfoTotal["fat"] += food["fat"] * food["mass"] / 100
                foodInfoTotal["saturated_fat"] += food["saturated_fat"] * food["mass"] / 100
                foodInfoTotal["carbohydrates"] += food["carbohydrates"] * food["mass"] / 100
                foodInfoTotal["sugar"] += food["sugar"] * food["mass"] / 100
                foodInfoTotal["fibre"] += food["fibre"] * food["mass"] / 100
                foodInfoTotal["protein"] += food["protein"] * food["mass"] / 100
                foodInfoTotal["salt"] += food["salt"] * food["mass"] / 100
                foodInfoTotal["price"] += food["price_per_kg"] * food["mass"] / 1000
                foodInfoTotal["mass"] += food["mass"]

            if "errorMsg" in session:
                errorMsg = session["errorMsg"]
                session.pop("errorMsg")
                return render_template("plan.html", info=info, plansList=get_plans(), foodList=get_foods(), foodInfo=foodInfo, foodInfoTotal=foodInfoTotal, errorMsg=errorMsg)
            elif "successMsg" in session:
                successMsg = session["successMsg"]
                session.pop("successMsg")
                return render_template("plan.html", info=info, plansList=get_plans(), foodList=get_foods(), foodInfo=foodInfo, foodInfoTotal=foodInfoTotal, successMsg=successMsg)
            else:
                return render_template("plan.html", info=info, plansList=get_plans(), foodList=get_foods(), foodInfo=foodInfo, foodInfoTotal=foodInfoTotal)


@app.route("/saveplan", methods=["GET", "POST"])
def saveplan():
    if request.method == "POST":
        # Gather infos
        info = {"planName": request.form.get("planNameInput", None, str),
                "dateTimeCreated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "dailyProteinEnergy": request.form.get("dailyProteinEnergyDisplay", -1, float),
                "dailyProteinMass": request.form.get("dailyProteinMassDisplay", -1, float),
                "dailyFatEnergy": request.form.get("dailyFatEnergyDisplay", -1, float),
                "dailyFatMass": request.form.get("dailyFatMassDisplay", -1, float),
                "dailyCarbEnergy": request.form.get("dailyCarbEnergyDisplay", -1, float),
                "dailyCarbMass": request.form.get("dailyCarbMassDisplay", -1, float),
                "dailyTotalEnergy": request.form.get("dailyTotalEnergyDisplay", -1, float)}
        # User circumvented the 'required' tag of input fields in one way or another and submitted insufficient information
        if not info["planName"]:
            session["errorMsg"] = "Please enter a name for the plan."
            return redirect("/plan")

        if (info["dailyProteinEnergy"] < 0 or
            info["dailyProteinMass"] < 0 or
            info["dailyFatEnergy"] < 0 or
            info["dailyFatMass"] < 0 or
            info["dailyCarbEnergy"] < 0 or
            info["dailyCarbMass"] < 0 or
            info["dailyTotalEnergy"] < 0):
            session["errorMsg"] = "Please verify valid macro values."
            return redirect("/plan")

        get_db("""INSERT INTO plans (plan_name,
                                    date_created,
                                    protein_energy,
                                    protein_mass,
                                    fat_energy,
                                    fat_mass,
                                    carbohydrate_energy,
                                    carbohydrate_mass,
                                    total_energy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (info["planName"],
                                                            info["dateTimeCreated"],
                                                            info["dailyProteinEnergy"],
                                                            info["dailyProteinMass"],
                                                            info["dailyFatEnergy"],
                                                            info["dailyFatMass"],
                                                            info["dailyCarbEnergy"],
                                                            info["dailyCarbMass"],
                                                            info["dailyTotalEnergy"]))
        session["successMsg"] = "Plan saved."
        return redirect("/plan")

    # User accessed route directly without submitting form
    else:
        return redirect("/plan")


@app.route("/loadplan", methods=["GET", "POST"])
def loadplan():
    if request.method == "POST":
        # Get user's action input
        action = request.form.get("planLoadDelete", None, str)
        plan_id = request.form.get("loadPlanName", None, str)
        # Action if user chose to load plan
        if action == "load":
            if plan_id != None:
                session["plan_id"] = plan_id
                session["successMsg"] = "Plan loaded."
            return redirect("/plan")
        # Action if user chose to delete plan
        elif action == "delete":
            if plan_id != None:
                get_db("DELETE FROM plans WHERE plan_id = ?", (plan_id,))
                get_db("DELETE FROM plan_food_link WHERE plan_id = ?", (plan_id,))
                session["successMsg"] = "Plan deleted."
                if "plan_id" in session:
                    session.pop("plan_id")
            return redirect("/plan")
        else:
            return redirect("/plan")

    else:
        return redirect("/plan")


@app.route("/food", methods=["GET"])
def food():
    foods = get_db("""SELECT * FROM foods""")
    if "errorMsg" in session:
        errorMsg = session["errorMsg"]
        session.pop("errorMsg")
        return render_template("food.html", foods=foods, errorMsg=errorMsg)
    elif "successMsg" in session:
        successMsg = session["successMsg"]
        session.pop("successMsg")
        return render_template("food.html", foods=foods, successMsg=successMsg)
    else:
        return render_template("food.html", foods=foods)


@app.route("/savefood", methods=["GET", "POST"])
def savefood():
    if request.method == "POST":
        timeAdded = time.strftime("%Y-%m-%d %H:%M:%S")
        protein = request.form.get("foodProteinInput", -1, float)
        mass = request.form.get("foodMassInput", -1, float)
        price = request.form.get("foodPriceInput", -1, float)
        get_db("""INSERT INTO foods (food_name,
                                    date_added,
                                    type,
                                    energy,
                                    fat,
                                    saturated_fat,
                                    carbohydrates,
                                    sugar,
                                    fibre,
                                    protein,
                                    salt,
                                    mass,
                                    price,
                                    price_per_kg,
                                    price_per_20g_protein,
                                    link,
                                    notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (request.form.get("foodNameInput", None, str),
                                                                                    timeAdded,
                                                                                    request.form.get("foodTypeInput", None, str),
                                                                                    request.form.get("foodEnergyInput", -1, float),
                                                                                    request.form.get("foodFatInput", -1, float),
                                                                                    request.form.get("foodSatFatInput", -1, float),
                                                                                    request.form.get("foodCarbInput", -1, float),
                                                                                    request.form.get("foodSugarInput", -1, float),
                                                                                    request.form.get("foodFibreInput", -1, float),
                                                                                    protein,
                                                                                    request.form.get("foodSaltInput", -1, float),
                                                                                    mass,
                                                                                    price,
                                                                                    price * 1000 * 1/mass,
                                                                                    price * 2000 * 1/(protein * mass),
                                                                                    request.form.get("foodLinkInput", None, str),
                                                                                    request.form.get("foodNotesInput", None, str)
                                                                                    ))
        session["successMsg"] = "Successfully added food."
        return redirect("/food")
    else:
        return redirect("/food")


@app.route("/deletefood", methods=["GET", "POST"])
def deletefood():
    if request.method == "POST":
        food_id = request.form.get("food_id", None, int)
        get_db("DELETE FROM foods WHERE food_id = ?", (food_id,))
        get_db("DELETE FROM plan_food_link WHERE food_id = ?", (food_id,))
        session["successMsg"] = "Food deleted."
        return redirect("/food")
    else:
        return redirect("/food")
    

@app.route("/addfoodtoplan", methods=["GET", "POST"])
def addfoodtoplan():
    if request.method == "POST":
        foodToAdd = request.form.get("foodToAdd", None, str)
        if foodToAdd == None:
            session["errorMsg"] = "Select food to add."
            return redirect("/plan")
        get_db("""INSERT INTO plan_food_link (plan_id,
                                                food_id,
                                                mass)
                    VALUES (?, ?, ?)""", (session["plan_id"], foodToAdd, 0))
        session["successMsg"] = "Food added to plan."
        return redirect("/plan")
    else:
        return redirect("/plan")
    

@app.route("/removefoodfromplan", methods=["GET", "POST"])
def removefoodfromplan():
    if request.method == "POST":
        food_id = request.form.get("food_id", None, int)
        get_db("""DELETE FROM plan_food_link WHERE plan_id = ? AND food_id = ?""", (session["plan_id"], food_id))
        session["successMsg"] = "Food removed from plan."
        return redirect("/plan")
    else:
        return redirect("/plan")
    

@app.route("/updatefoodmass", methods=["GET", "POST"])
def updatefoodmass():
    if request.method == "POST":
        newMass = request.form.get("planFoodMass")
        food_id = request.form.get("food_id")
        get_db("""UPDATE plan_food_link
                    SET mass = ?
                    WHERE plan_id = ? AND food_id = ?""", (newMass, session["plan_id"], food_id))
        session["successMsg"] = "Mass updated."
        return redirect("/plan")
    else:
        return redirect("/plan")