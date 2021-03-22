import os
import subprocess
import matplotlib.pyplot as plt
import json

from app import app
from app.util import Ephemeris, StateData
from flask import render_template, request, redirect, session

app.config["SECRET_KEY"] = "-2YdMLd8a8AKlPKHWdgbMw"


directory = os.path.join(app.root_path)
data = "\\ephemeris\\data\\state_processed_cassini.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return "<h1 style='color: red'>About!!!!!</h1>"

@app.route("/ephemeris/")
def ephemeris():
    return redirect("/ephemeris/run")

@app.route("/ephemeris/run")
def ephemeris_run():
    return render_template("ephemeris.html", navigation="run")

@app.route("/ephemeris/build")
def ephemeris_build():
    return render_template("ephemeris.html", navigation="build")

@app.route("/ephemeris/process", methods=["GET", "POST"])
def ephemeris_process():
    # load, options-processed, options-kerbal
    # delete, options-processed, options-kerbal
    # process scale, options, and no options
    # display loaded files, then processed file

    data = {
        "files": {},
        "list_data": []
    }

    if request.method == "POST":
        req = request.form
        if request.files:
            upload_file = request.files["upload-file"]
            if "processed" in req:
                upload_file.save(os.path.join(directory + "\\ephemeris\\input\\processed\\", upload_file.filename))
            else:
                upload_file.save(os.path.join(directory + "\\ephemeris\\input\\kerbal\\", upload_file.filename))

        elif request.form:
            if req["submit_button"] == "delete-file":
                if "options-load" in req:
                    options_load = req["options-load"]

                    if options_load[len(options_load) - 4:] == ".pro":
                        os.remove(directory + "\\ephemeris\\input\\processed\\" + options_load[0:len(options_load) - 4:])

                    if options_load[len(options_load) - 4:] == ".ksp":
                        os.remove(directory + "\\ephemeris\\input\\kerbal\\" + options_load[0:len(options_load) - 4:])   

            if req["submit_button"] == "load-file":
                    if "options-load" in req:
                        options_load = req["options-load"]

                        if options_load[len(options_load) - 4:] == ".pro":
                            initial_states = StateData(directory + "\\ephemeris\\input\\processed\\" + options_load[0:len(options_load) - 4:], False)
                            data["list_data"] = initial_states.list_data()
                            session["loaded_file"] = directory + "\\ephemeris\\input\\processed\\" + options_load[0:len(options_load) - 4:]
                            session["loaded_file_type"] = "processed"

                        if options_load[len(options_load) - 4:] == ".ksp":
                            initial_states = StateData(directory + "\\ephemeris\\input\\kerbal\\" + options_load[0:len(options_load) - 4:], True)
                            data["list_data"] = initial_states.list_data()
                            session["loaded_file"] = directory + "\\ephemeris\\input\\kerbal\\" + options_load[0:len(options_load) - 4:]
                            session["loaded_file_type"] = "kerbal"

            if req["submit_button"] == "process":
               if "loaded_file" in session:
                   process_data = dict(request.form.lists())
                   process_data["loaded_file_type"] = session["loaded_file_type"]

                   if session["loaded_file_type"] == "processed":
                       initial_states = StateData(session["loaded_file"], False)                
                   else:
                       initial_states = StateData(session["loaded_file"], True)
                       session["loaded_file_type"] = "processed"
                    
                   session["loaded_file"] = directory + "\\ephemeris\\input\\processed\\" + process_data["filename"][0] + ".json"

                   processed_json = initial_states.process(process_data)

                   with open(directory + "\\ephemeris\\input\\processed\\" + process_data["filename"][0] + ".json", "w") as output_file:
                        output_file.write(json.dumps(processed_json, indent=4))


    if "loaded_file" in session:
        if os.path.exists(session["loaded_file"]):
            if session["loaded_file_type"] == "processed":
                initial_states = StateData(session["loaded_file"], False)
                data["list_data"] = initial_states.list_data()

            if session["loaded_file_type"] == "kerbal":
                initial_states = StateData(session["loaded_file"], True)
                data["list_data"] = initial_states.list_data()

    data["files"] = {
        "kerbal files": os.listdir(directory + "\\ephemeris\\input\\kerbal"),
        "processed files": os.listdir(directory + "\\ephemeris\\input\\processed")}
  
    return render_template("ephemeris.html", navigation="process", data=data)

@app.route("/flightplan")
def flightplan():
    return render_template("flightplan.html")

@app.route("/visualize")
def visualize():
    return render_template("visualize.html")




