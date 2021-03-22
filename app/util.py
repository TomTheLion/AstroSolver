import subprocess
import app.ksp as ksp
import numpy as np
import json

class Ephemeris:
    def __init__(self, input_file_directory, output_file_directory, ephemeris_inputs):
        self.build_ephemeris_exe = ephemeris_inputs["build_ephemeris_exe"]
        self.build_ephemeris_input_file = input_file_directory + ephemeris_inputs["loaded_build_ephemeris_input_file"]
        self.ephemeris_file = output_file_directory + ephemeris_inputs["ephemeris_file"]
        self.num_steps = ephemeris_inputs["num_steps"]
        self.step_length = ephemeris_inputs["step_length"]
        self.i_tol = ephemeris_inputs["i_tol"]
        self.e_tol = ephemeris_inputs["e_tol"]

    def build_ephemeris(self):
        p = subprocess.Popen([
            self.build_ephemeris_exe, 
            self.build_ephemeris_input_file,
            self.ephemeris_file,
            self.num_steps,
            self.step_length,
            self.i_tol,
            self.e_tol], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

        stderr = p.communicate()[1].decode("utf-8").splitlines()
        stdout = p.communicate()[0].decode("utf-8").splitlines()

        return p.returncode, stderr + stdout

class StateData:
    def __init__(self, file_path, from_ksp=False):
        with open(file_path) as input_file:
            if from_ksp:
                self.data = ksp.from_ksp(json.load(input_file))
            else:
                self.data = json.load(input_file)
        self.from_ksp = from_ksp
        self.keep_list = []
        self.astronomical_unit = 149597870700

    def list_data(self):

        if self.from_ksp:
            colwidth = 14

            lst = []
            lst.append(["", "Body".ljust(colwidth) + "Primary".ljust(colwidth) + "mu (m^3/s^2)".ljust(colwidth) + "posision (x, y, z) (m)".ljust(3 * colwidth) + "velocity (x, y, z) (m/s)".ljust(3 * colwidth), 0])
            lst.append(["Sun", self.format_output_kerbal(colwidth, "Sun", "", self.data["bodies"]["Sun"]), 0])

            planets = self.data["bodies"]["planets"]
            for planet in planets:
                lst.append([planet, self.format_output_kerbal(colwidth, planet, "Sun", planets[planet]), 1])
                satellites = planets[planet]["satellites"]
                for satellite in satellites:
                    lst.append([satellite, self.format_output_kerbal(colwidth, satellite, planet, satellites[satellite]), 0])


            # lst.append("Primary + ")
            # print(self.data["bodies"].keys())
            # print(self.data["bodies"]["planets"].keys())
            # for body in self.data["bodies"]["planets"]:
            #     print(self.data["bodies"]["planets"][body]['satellites'].keys())
        else:
            colwidth = 14

            lst = []
            lst.append(["", "Info:", 0])
            for item in self.data["info"]:
                lst.append(["", item.ljust(colwidth) + "{: 10.4e}".format(float(self.data["info"][item])).ljust(colwidth), 0])
            lst.append(["", "", 0])           

            lst.append(["", "Body".ljust(colwidth) + "mu (m^3/s^2)".ljust(colwidth) + "posision (x, y, z) (m)".ljust(3 * colwidth) + "velocity (x, y, z) (m/s)".ljust(3 * colwidth), 0])
            lst.append([self.data["primary"]["name"], self.format_output_processed(colwidth, self.data["primary"]["name"], self.data["primary"]), 0])

            for body in self.data["bodies"]:
                lst.append([body["name"], self.format_output_processed(colwidth, body["name"], body), 1])

        return lst

    def process(self, params):
        if params["loaded_file_type"] == "processed":
            return self.process_processed(params)
        else:
            return self.process_kerbal(params)

    def process_processed(self, params):
        
        distance_scale = 1.0
        time_scale = 1.0

        if params["scale"][0] == "km-s":
            distance_scale = 1000
            time_scale = 1.0
        if params["scale"][0] == "au-year":
            distance_scale = 149597870700
            time_scale = 31558149
        if params["scale"][0] == "au-2piyear":
            distance_scale = 149597870700
            time_scale = 5022635.40818055
        if params["scale"][0] == "kau-kyear":
            distance_scale = 13599840256
            time_scale = 9203545

        # calculate scale factors
        mu_scale = distance_scale ** 3 / time_scale ** 2
        velocity_scale = distance_scale / time_scale

        # create output dictionary
        self.data["info"] = {
            "time": self.data["info"]["time"],
            "mu_scale": mu_scale,
            "distance_scale": distance_scale,
            "time_scale": time_scale,
            "velocity_scale": velocity_scale
        }

        remove = []
        if "options" in params:
            remove = params["options"]

        for body in remove:
            for body_data in self.data["bodies"]:
                if body == body_data["name"]:
                    self.data["bodies"].remove(body_data)
                    break

        return self.data

    def process_kerbal(self, params):
        sun = self.data["bodies"]["Sun"]
        planets = self.data["bodies"]["planets"]
        solar_prime_vector = self.data["bodies"]["Sun"]["solar prime vector"]

        rotation_angle = np.arctan2(solar_prime_vector[2], solar_prime_vector[0])

        distance_scale = 1.0
        time_scale = 1.0

        if params["scale"][0] == "km-s":
            distance_scale = 1000
            time_scale = 1.0
        if params["scale"][0] == "au-year":
            distance_scale = 149597870700
            time_scale = 31558149
        if params["scale"][0] == "au-2piyear":
            distance_scale = 149597870700
            time_scale = 5022635.40818055
        if params["scale"][0] == "kau-kyear":
            distance_scale = 13599840256
            time_scale = 9203545

        # calculate scale factors
        mu_scale = distance_scale ** 3 / time_scale ** 2
        velocity_scale = distance_scale / time_scale

        # create output dictionary
        ephemeris_input = {}

        ephemeris_input["info"] = {
            "time": self.data["time"],
            "mu_scale": mu_scale,
            "distance_scale": distance_scale,
            "time_scale": time_scale,
            "velocity_scale": velocity_scale
        }

        ephemeris_input["primary"] = {
            "name": "Sun",
            "mu": sun["mu"],
            "state": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
            ]
        }
        ephemeris_input["bodies"] = []

        keep = []
        if "options" in params:
            keep = params["options"]

        for planet, planet_data in planets.items():
            # keep moons of desired planets
            if planet in keep:
                position = self.vector_axis_angle(np.array(planet_data["position"]), [0, 1, 0], rotation_angle)
                velocity = self.vector_axis_angle(np.array(planet_data["velocity"]), [0, 1, 0], rotation_angle)
                state = list(position) + list(velocity)
                ephemeris_input["bodies"].append(
                    {
                        "name": planet,
                        "state": state,
                        "mu": planet_data["mu"]
                    }
                )
                for satellite, satellite_data in planet_data["satellites"].items():
                    position = self.vector_axis_angle(np.array(satellite_data["position"]), [0, 1, 0], rotation_angle)
                    velocity = self.vector_axis_angle(np.array(satellite_data["velocity"]), [0, 1, 0], rotation_angle)
                    state = list(position) + list(velocity)
                    ephemeris_input["bodies"].append(
                        {
                            "name": satellite,
                            "state": state,
                            "mu": satellite_data["mu"]
                        }
                    )
            # mass weighted average of planet/moon systems
            else:
                position = planet_data["mu"] * self.vector_axis_angle(np.array(planet_data["position"]), [0, 1, 0], rotation_angle)
                velocity = planet_data["mu"] * self.vector_axis_angle(np.array(planet_data["velocity"]), [0, 1, 0], rotation_angle)
                mu = planet_data["mu"]
                for satellite_data in planet_data["satellites"].values():
                    position += satellite_data["mu"] * self.vector_axis_angle(np.array(satellite_data["position"]), [0, 1, 0], rotation_angle)
                    velocity += satellite_data["mu"] * self.vector_axis_angle(np.array(satellite_data["velocity"]), [0, 1, 0], rotation_angle)
                    mu += satellite_data["mu"]
                position /= mu
                velocity /= mu
                state = list(position) + list(velocity)

                ephemeris_input["bodies"].append(
                    {
                        "name": planet,
                        "state": state,
                        "mu": mu
                    }
                )

        return ephemeris_input  

    @staticmethod
    def format_output_kerbal(colwidth, body, primary, data):
        mu = "{: 10.4e}".format(data["mu"])
        r = "{: 10.4e}".format(data["position"][0]) + ", " + "{: 10.4e}".format(data["position"][1]) + ", " + "{: 10.4e}".format(data["position"][2])
        v = "{: 10.4e}".format(data["velocity"][0]) + ", " + "{: 10.4e}".format(data["velocity"][1]) + ", " + "{: 10.4e}".format(data["velocity"][2])        
        return body.ljust(colwidth) + primary.ljust(colwidth) + mu.ljust(colwidth) + r.ljust(3 * colwidth) + v.ljust(3 * colwidth)

    @staticmethod
    def format_output_processed(colwidth, body, data):
        mu = "{: 10.4e}".format(data["mu"])
        r = "{: 10.4e}".format(data["state"][0]) + ", " + "{: 10.4e}".format(data["state"][1]) + ", " + "{: 10.4e}".format(data["state"][2])
        v = "{: 10.4e}".format(data["state"][3]) + ", " + "{: 10.4e}".format(data["state"][4]) + ", " + "{: 10.4e}".format(data["state"][5])        
        return body.ljust(colwidth) + mu.ljust(colwidth) + r.ljust(3 * colwidth) + v.ljust(3 * colwidth)

    @staticmethod
    def vector_axis_angle(vector, axis, angle):
        axis = axis / np.linalg.norm(axis)
        return vector * np.cos(angle) + np.cross(axis, vector) * np.sin(angle) + axis * np.dot(axis, vector) * (1 - np.cos(angle))

    
