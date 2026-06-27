from flask import Flask, render_template_string, request, redirect
import os, subprocess
from injector import build_final_workflow
from sandbox import start_sandbox, stop_sandbox

app = Flask(__name__)

BASE = os.getcwd()
SERVER = BASE + "/server"
UPLOADS = BASE + "/uploads"

os.makedirs(SERVER, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

HTML = """
<!doctype html>
<html>
<head>
<title>MC Server Builder</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="card">
<h1>Minecraft Server Builder</h1>

<form action="/upload" method="post" enctype="multipart/form-data">
<h3>Upload server.jar / mods / plugins</h3>
<input type="file" name="file" multiple>
<button>Upload</button>
</form>

<form action="/sandbox" method="post">
<h3>Test in Sandbox</h3>
<input name="java" placeholder="-Xmx2G -Xms1G" value="-Xmx2G -Xms1G">
<button>Run Test</button>
<button formaction="/sandbox/stop">Force Kill</button>
</form>

<form action="/build" method="post">
<h3>Build Final Server</h3>
<input name="jvm" placeholder="-Xmx6G -Xms6G">
<button class="green">BUILD</button>
</form>

<h3>Files</h3>
<pre>{{files}}</pre>

</div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, files="\n".join(os.listdir(SERVER)))

@app.route("/upload", methods=["POST"])
def upload():
    for f in request.files.getlist("file"):
        f.save(os.path.join(SERVER, f.filename))
    return redirect("/")

@app.route("/sandbox", methods=["POST"])
def sandbox():
    start_sandbox(request.form["java"])
    return redirect("/")

@app.route("/sandbox/stop", methods=["POST"])
def sandbox_stop():
    stop_sandbox()
    return redirect("/")

@app.route("/build", methods=["POST"])
def build():
    build_final_workflow(request.form["jvm"])
    return "Final workflow created ✔"

app.run("0.0.0.0", 8000)
