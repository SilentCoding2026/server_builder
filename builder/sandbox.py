import subprocess, os, signal

PID_FILE = "/tmp/mc_sandbox.pid"

def start_sandbox(jvm):
    jar = next(f for f in os.listdir("server") if f.endswith(".jar"))
    p = subprocess.Popen(
        f"java {jvm} -jar server/{jar} nogui",
        shell=True,
        preexec_fn=os.setsid
    )
    open(PID_FILE, "w").write(str(p.pid))

def stop_sandbox():
    if os.path.exists(PID_FILE):
        pid = int(open(PID_FILE).read())
        os.killpg(pid, signal.SIGKILL)
