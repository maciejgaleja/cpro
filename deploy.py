import os
import subprocess
import datetime
import shutil
import sys


def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def main():
    version = subprocess.check_output(
        ["git", "describe", "--tags"]).decode("utf-8").split("\n")[0]
    print(version)
    with open("cpro/version.py", "w") as f:
        f.write("version=\"" + version +
                " (built " + datetime.datetime.now().isoformat() + ")\"")

    if '--version-only' in sys.argv:
        exit(0)

    mypy_result = subprocess.run(
        ["mypy", "--config-file", "../config.mypy", "cpro.py"], cwd="./cpro/")
    if not mypy_result.returncode == 0:
        exit(mypy_result.returncode)

    subprocess.run(["pyinstaller", "cpro.py", "--clean", "-F"], cwd="./cpro/")

    date_time_str = datetime.datetime.now().strftime("%Y-%m-%d")
    deploy_dir_name = "_deploy/" + date_time_str
    ensure_dir_exists(deploy_dir_name)

    if os.name == 'nt':
        shutil.copyfile("cpro/dist/cpro.exe", deploy_dir_name + "/cpro.exe")
    else:
        shutil.copyfile("cpro/dist/cpro", deploy_dir_name + "/cpro")

    shutil.rmtree("cpro/build")
    shutil.rmtree("cpro/dist")
    os.remove("cpro/cpro.spec")


if __name__ == '__main__':
    main()
