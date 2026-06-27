from flask import Flask, render_template_string, request, redirect
import os, subprocess, traceback
from injector import build_final_workflow
from sandbox import start_sandbox, stop_sandbox
import requests
app = Flask(__name__)

BASE = os.getcwd()
SERVER = BASE + "/server"
UPLOADS = BASE + "/uploads"
BUILD_SIGNAL = BASE + "/.build_triggered"

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
<div class="container">
<div class="card">
<h1>Minecraft Server Builder</h1>

<div class="section">
<h3>Upload local files</h3>
<form action="/upload" method="post" enctype="multipart/form-data" class="form-row">
  <input type="file" name="file" multiple>
  <button>Upload</button>
</form>
</div>

<div class="section">
<h3>Get file from URL</h3>
<form action="/fetch" method="post" class="form-row">
  <input name="url" placeholder="https://example.com/file.jar" required>
  <input name="filename" placeholder="server.jar (or mod.jar)" required>
  <input name="path" placeholder="./ or mods or plugins">
  <button>Download</button>
</form>
</div>

<div class="section">
<h3>Test in Sandbox</h3>
<form action="/sandbox" method="post" class="form-row">
  <input name="java" value="-Xmx2G -Xms1G">
  <button>Run Test</button>
  <button formaction="/sandbox/stop" class="red">Force Kill</button>
</form>
</div>

<div class="section">
<h3>Build Final Server</h3>
<form action="/build" method="post" class="form-row">
  <input name="jvm" value="-Xmx6G -Xms6G">
  <button class="green">BUILD</button>
</form>
</div>

<div class="section">
<h3>Server files</h3>
<pre>{{files}}</pre>
</div>

</div>
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
    try:
        build_final_workflow(request.form["jvm"])
    except Exception as e:
        traceback.print_exc()
    open(BUILD_SIGNAL, "w").write("done")
    os._exit(0)

@app.route("/fetch", methods=["POST"])
def fetch():
    url = request.form["url"]
    filename = request.form["filename"]
    path = request.form.get("path", "").strip()

    if path in ("", ".", "./"):
        target_dir = SERVER
    else:
        target_dir = os.path.join(SERVER, path)

    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, filename)

    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()

    with open(target_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return redirect("/")

app.run("0.0.0.0", 8000)
