import os
import subprocess
import datetime
import shutil


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

    subprocess.run(["pyinstaller", "cpro.py", "--clean", "-F"], cwd="./cpro/")

    date_time_str = datetime.datetime.now().strftime("%Y-%m-%d")
    deploy_dir_name = "_deploy/" + date_time_str
    ensure_dir_exists(deploy_dir_name)

    shutil.copyfile("cpro/dist/cpro", deploy_dir_name + "/cpro")

    shutil.rmtree("cpro/build")
    shutil.rmtree("cpro/dist")
    os.remove("cpro/cpro.spec")


if __name__ == '__main__':
    main()
