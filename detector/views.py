from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for

import time, random
import requests
import io
import tempfile
import os
from datetime import datetime

detector = Blueprint("detector", __name__)

class TempDetector:
    running = False
    started_running = time.time()
    status = "OK"
    last_check_time = 0
    total_muons = 0

    @staticmethod
    def start():
        TempDetector.started_running = time.time()
        TempDetector.total_muons = 0
        TempDetector.last_check_time = 0
        TempDetector.running = True

    @staticmethod
    def running_for():
        return time.time()-TempDetector.started_running

    @staticmethod
    def running_for_hms():
        t = time.time()-TempDetector.started_running
        h, m = divmod(t, 3600)
        m, s = divmod(m, 60)
        return (int(h), int(m), s)


def generate_pretend_file(muons):
    file = tempfile.NamedTemporaryFile(delete=False)
    filename = file.name
    file.close()
    print(filename)
    with open(filename, "w") as file:
        for i in range(0, muons):
            xi, yi, zi = round(0.05 + 0.1*random.randint(0, 9), 2), round(0.05 + 0.1*random.randint(0, 9), 2), 1
            while True:
                xf, yf, zf = round(xi+(0.1*random.randint(0, 6)-0.3), 2), round(yi+(0.1*random.randint(0, 6)-0.3), 2), 0
                if 0 < xf < 1 and 0 < yf < 1:
                    break
            file.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(xi, yi, zi, xf, yf, zf))
    return open(filename, "r")

@detector.route("/detector", methods=["GET", "POST"])
def detector_status():
    if request.method == "POST":
        if request.form["submit"] == "start":
            TempDetector.start()
            flash("Detector started.", "success")
        if request.form["submit"] == "stop":
            TempDetector.running = False
            flash("Detector stopped. Total run time was {0}h {1}m {2:.02f}s.".format(*TempDetector.running_for_hms()), "success")

            with generate_pretend_file(TempDetector.total_muons) as file:
                data = {"detector_start_time":TempDetector.started_running,
                        "detector_end_time":time.time()}
                req = requests.post("http://127.0.0.1:5000/upload_result", files={"name":file}, data=data)
                if req.ok:
                    flash("File uploaded", "success")
                    return redirect(url_for("result.result_page", result_id=req.json()["result_id"]))
                else:
                    flash("File not uploaded", "error")
            #os.unlink(filename)

        # Don't want to repost form on a page refresh
        return redirect(url_for("detector.detector_status"))
    return render_template("detector_status.html", status=TempDetector.status, current_seconds=int(TempDetector.running_for()), run_time="{0}h {1}m {2:.02f}s".format(*TempDetector.running_for_hms()), detector_running=TempDetector.running)

@detector.route("/current_muons")
def current_muons():
    if TempDetector.running:
        for i in range(0, int((TempDetector.running_for()-TempDetector.last_check_time)*100)):
            if random.random() > 0.8:
                TempDetector.total_muons += 1
        TempDetector.last_check_time = TempDetector.running_for()
    else:
        flash("Detector is no longer running.", "error")
    return jsonify(result=TempDetector.total_muons, reload= not TempDetector.running)