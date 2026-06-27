import os, subprocess, json
from utils import make_eula

def build_final_workflow(jvm):
    make_eula("server")

    # ساخت بکاپ اولیه
    subprocess.run("rm -f server_backup.7z*", shell=True)
    subprocess.run("7z a server_backup.7z server", shell=True)
    subprocess.run("7z a server_backup.7z.part server_backup.7z -v95m", shell=True)

    # خواندن تنظیمات
    state = json.load(open("builder/server_state.json"))
    jar = state["server_jar"]

    # ساخت workflow نهایی
    tpl = open("templates/final_server.yml.tpl").read()
    tpl = tpl.replace("{{JVM}}", jvm)
    tpl = tpl.replace("{{SERVER_JAR}}", jar)

    os.makedirs(".github/workflows", exist_ok=True)
    wf_path = ".github/workflows/final_server.yml"
    open(wf_path, "w").write(tpl)

    # 👇👇👇 بسیار مهم
    subprocess.run("git config user.name 'github-actions[bot]'", shell=True)
    subprocess.run("git config user.email 'github-actions[bot]@users.noreply.github.com'", shell=True)
    subprocess.run(f"git add {wf_path}", shell=True)
    subprocess.run("git commit -m 'add final server workflow'", shell=True)
    subprocess.run("git push", shell=True)
