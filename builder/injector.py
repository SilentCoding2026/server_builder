import os, subprocess
from utils import make_eula

def build_final_workflow(jvm):
    make_eula("server")

    subprocess.run("rm -f server_backup.7z*", shell=True)
    subprocess.run("7z a server_backup.7z server", shell=True)
    subprocess.run("7z a server_backup.7z.part server_backup.7z -v95m", shell=True)

    tpl = open("templates/final_server.yml.tpl").read()
    tpl = tpl.replace("{{JVM}}", jvm)

    os.makedirs(".github/workflows", exist_ok=True)
    open(".github/workflows/final_server.yml", "w").write(tpl)
