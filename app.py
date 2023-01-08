# Imports

from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # Response to POST request (user submitted input)
    if request.method == "POST":
        # Gather info from form
        info = {"targetCal": request.form.get("targetCal", -1, int),
                "fatPercent": request.form.get("fatPercent", -1, int),
                "proteinMass": request.form.get("proteinMass", -1, int)}
        # Return error for invalid input
        errorMsg = "Please enter a positive number for: "
        error = False
        for key, value in info.items():
            if value < 0:
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
        # Render index page with values in info
        return render_template("index.html", info=info)
    # Response to GET request
    else:
        return render_template("index.html")
