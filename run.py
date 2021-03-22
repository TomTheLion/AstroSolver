from app import app

if __name__ == "__main__":
    app.run()

# from flask import Flask
# import numpy as np

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return str(np.cos(69))

# if __name__ == "__main__":
#     app.run()

# @app.route("/about")
# def about():
#     return "<h1 style='color: red'>About!!!!!</h1>"

# import io
# import os
# import random
# import subprocess
# from flask import Flask
# from flask import Response, render_template
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure

# app = Flask(__name__)

# directory = os.path.join(app.root_path)

# @app.route('/plot.png')
# def plot_png():
#     fig = create_figure()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')

# def create_figure():
#     fig = Figure()
#     axis = fig.add_subplot(1, 1, 1)
#     xs = range(100)
#     ys = [random.randint(1, 50) for x in xs]
#     axis.plot(xs, ys)
#     return fig

# def build_ephemeris(directory, data):
#     input_file = directory + data
#     output_file = directory + "\\ephemeris\\eph824"
#     num_steps = "2000"
#     step_length = "0.10"
#     i_tol = "1e-13"
#     e_tol = "1e-10"

#     p = subprocess.Popen([directory + "\\ephemeris\\BuildEphemeris.exe", input_file, output_file, num_steps, step_length, i_tol, e_tol])
#     p.wait()

# # build_ephemeris(directory, "\\ephemeris\\data\\state_processed_cassini.json")

# @app.route("/upload-ephemeris-data", methods=["GET", "POST"])
# def upload_ephemeris_data():
#     return render_template("upload_ephemeris_data.html")