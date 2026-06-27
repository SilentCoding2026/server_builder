import os, subprocess, json
from utils import make_eula

def build_final_workflow(jvm):
    make_eula("server")

    subprocess.run("rm -f server_backup.7z*", shell=True)
    subprocess.run("7z a server_backup.7z server", shell=True)
    subprocess.run("7z a server_backup.7z.part server_backup.7z -v95m", shell=True)

    state_path = "builder/server_state.json"
    if os.path.exists(state_path):
        state = json.load(open(state_path))
        jar = state["server_jar"]
    else:
        jars = [f for f in os.listdir("server") if f.endswith(".jar")]
        jar = jars[0] if jars else "server.jar"

    tpl = open("templates/final_server.yml.tpl").read()
    tpl = tpl.replace("{{JVM}}", jvm)
    tpl = tpl.replace("{{SERVER_JAR}}", jar)

    os.makedirs(".github/workflows", exist_ok=True)
    wf_path = ".github/workflows/final_server.yml"
    open(wf_path, "w").write(tpl)

    subprocess.run("git config user.name 'github-actions[bot]'", shell=True)
    subprocess.run("git config user.email 'github-actions[bot]@users.noreply.github.com'", shell=True)
    subprocess.run(f"git add {wf_path}", shell=True)
    subprocess.run("git commit -m 'add final server workflow'", shell=True)
    subprocess.run("git push", shell=True)

    subprocess.run("gh release delete latest --yes || true", shell=True)
    subprocess.run("gh release create latest server_backup.7z.part*", shell=True)
