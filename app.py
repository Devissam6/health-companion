# Imports

from flask import Flask, redirect, render_template, request
import sqlite3
import time

app = Flask(__name__)

DATABASE = 'foodData.db'

def get_db(query, args=(), one=False):
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.row_factory = sqlite3.Row

    res = cur.execute(query, args).fetchall()
    db.commit()
    db.close()

    return (res[0] if res else None) if one else res

def get_plans():
    return get_db("SELECT * FROM plans")


@app.route("/", methods=["GET", "POST"])
def index():
    # Response to POST request (user submitted input)
    if request.method == "POST":
        # Gather info from form
        info = {"targetCal": request.form.get("targetCal", -1, float), 
                "proteinMass": request.form.get("proteinMass", -1, float),
                "fatPercent": request.form.get("fatPercent", -1, float)}
        # Return error for invalid input
        errorMsg = "Invalid input for: "
        error = False
        for key, value in info.items():
            if (value < 0 or
                (key == "proteinMass" and value > (1/4) * info["targetCal"]) or
                (key == "fatPercent" and ((value/100) * info["targetCal"] > info["targetCal"] - 4 * info["proteinMass"] or value > 100) and "proteinMass" not in errorMsg)):
                errorMsg += ("({error}) ".format(error=key))
                error = True
        if error:
            return render_template("index.html", errorMsg=errorMsg)
        # Calculate values to fill table
        info["proteinEnergy"] = info["proteinMass"] * 4
        info["fatEnergy"] = info["targetCal"] * (info["fatPercent"]/100)
        info["fatMass"] = info["fatEnergy"] * (1/9)
        info["carbEnergy"] = info["targetCal"] - info["proteinEnergy"] - info["fatEnergy"]
        info["carbMass"] = info["carbEnergy"] * (1/4)
        info["totalEnergy"] = info["targetCal"]
        # Render index page with values in info, retrieved plans from database
        return render_template("index.html", info=info, plansList=get_plans())
    # Response to GET request
    else:
        # Retrieve all plans from database
        return render_template("index.html", plansList=get_plans())


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
            return render_template("index.html", errorMsg="Please enter a name for the plan.")
        if (info["dailyProteinEnergy"] < 0 or
            info["dailyProteinMass"] < 0 or
            info["dailyFatEnergy"] < 0 or
            info["dailyFatMass"] < 0 or
            info["dailyCarbEnergy"] < 0 or
            info["dailyCarbMass"] < 0 or
            info["dailyTotalEnergy"] < 0):
            return render_template("index.html", errorMsg="Please verify valid macro values.")

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

        return redirect("/")

    # User accessed route directly without submitting form
    else:
        return redirect("/")


@app.route("/loadplan", methods=["GET", "POST"])
def loadplan():
    if request.method == "POST":
        plan_id = request.form.get("loadPlanName", None, str)
        res = get_db("SELECT * FROM plans WHERE plan_id = ?", (plan_id))[0]

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
        return render_template("index.html", info=info, plansList=get_plans())
    else:
        return redirect("/")

