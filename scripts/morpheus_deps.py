import subprocess


def who_needs(package_name):
    cmd = f"conda-tree whoneeds {package_name}"
    rc = subprocess.check_output(cmd, shell=True)
    rc = rc.decode("utf-8").split("\n")
    return rc


def process_one_output(tmp_package, tree):
    # recursively check who needs the package
    while True:
        if tmp_package == "python":
            continue
        if tmp_package:
            tree.append(tmp_package)
        if not tmp_package or tmp_package == "morpheus":
            break
    print(" ".join(tree))

    return child_package

def process_output(tmp_package, tree):



def main():
    # list of packages to check
    packages = ["atk-1.0", "xz"]
    for package in packages:
        tree = [f"conda-tree {package}"]
        print(f"Checking who needs {package}")
        tmp_package = package
        rc = who_needs(tmp_package)
        # recursively check who needs the package
        for tmp_package in rc:
            process_output(tmp_package, tree)

if __name__ == "__main__":
    main()
