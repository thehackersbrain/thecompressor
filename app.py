import gzip
import hashlib
import os
import subprocess
from time import strftime

from flask import Flask, render_template, request, send_file

# app configuration
app = Flask(__name__, static_url_path="/static")
app.secret_key = os.urandom(32)

counter = 0


@app.route("/", methods=["GET", "POST"])
def compress():
    global counter

    if request.method == "GET":
        results = None
        return render_template("index.html", results=results)
    else:
        results = None
        if counter >= 10:
            os.system("/bin/rm /tmp/*.gz")
            counter = 0

        filename = ""
        contents = ""
        if "filename" in request.form:
            filename = request.form["filename"]
            if "contents" in request.form:
                contents = request.form["contents"]

        reqData = ["filename", "contents"]

        for i in reqData:
            if not request.form[i]:
                data = str(i)
                return render_template(
                    "index.html", error=data, results=results
                )  # "{} field is empty...".format(str(i))

        if not filename.endswith(".gz"):
            status = 1
            return render_template(
                "index.html", status=str(status), results=results
            )  # "filename must end with '.gz' extension..."

        with gzip.open("/tmp/{}".format(filename), "wb") as fh:
            fh.write(contents.encode("utf-8"))

        sha = hashlib.sha256()
        with open("/tmp/{}".format(filename), "rb") as fp:
            sha.update(fp.read())

        shahash = sha.hexdigest()

        prs = subprocess.Popen(
            "zgrep . *gz", shell=True, cwd="/tmp/", stdout=subprocess.PIPE
        )
        results = prs.stdout.read().decode("utf-8")

        counter += 1

        return render_template(
            "index.html", results=results, shahash=shahash, filename=filename
        )


@app.route("/download/<filename>")
def download(filename):
    if os.path.exists("/tmp/%s" % filename):
        return send_file(
            "/tmp/{}".format(filename), as_attachment=True, download_name=filename
        )
    else:
        return "Woops! That file doesn't exists..."


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
