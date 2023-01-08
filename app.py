# Imports

from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Gather info from form
        targetCal = int(request.form.get("targetCal"))
        fatPercent = int(request.form.get("fatPercent"))
        proteinMass = int(request.form.get("proteinMass"))
        info = {"targetCal": targetCal, "fatPercent": fatPercent, "proteinMass": proteinMass}

        info["proteinEnergy"] = proteinMass * 4
        info["fatEnergy"] = targetCal * (fatPercent/100)
        info["fatMass"] = info["fatEnergy"] * (1/9)
        info["carbEnergy"] = info["targetCal"] - info["proteinEnergy"] - info["fatEnergy"]
        info["carbMass"] = info["carbEnergy"] * (1/4)
        info["totalEnergy"] = info["targetCal"]

        return render_template("index.html", info=info)
    else:
        return render_template("index.html")
