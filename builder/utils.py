import os

def make_eula(path):
    open(os.path.join(path, "eula.txt"), "w").write("eula=true\n")
