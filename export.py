"""Build the client zip: packwiz CurseForge export + recommendedRam in manifest.json.

packwiz can't write minecraft.recommendedRam. Prism and the CurseForge app set the
instance's max memory from it on a fresh import (Prism clamps it to 90% of system RAM).
Usage: python export.py   ->  dist/<name>-<version>.zip
"""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile

RAM_MIB = 6144

root = os.path.dirname(os.path.abspath(__file__))
pack = open(os.path.join(root, "pack.toml"), encoding="utf-8").read()
name = re.search(r'^name = "(.*)"', pack, re.M).group(1).replace(" & ", "-and-").replace(" ", "-")
version = re.search(r'^version = "(.*)"', pack, re.M).group(1)
out = os.path.join(root, "dist", f"{name}-{version}.zip")
os.makedirs(os.path.dirname(out), exist_ok=True)

packwiz = shutil.which("packwiz") or os.path.join(
    subprocess.check_output(["go", "env", "GOPATH"], text=True).strip(), "bin", "packwiz")
subprocess.check_call([packwiz, "refresh"], cwd=root)
raw = tempfile.mktemp(suffix=".zip")
subprocess.check_call([packwiz, "curseforge", "export", "-o", raw], cwd=root)

with zipfile.ZipFile(raw) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "manifest.json":
            m = json.loads(data)
            m["minecraft"]["recommendedRam"] = RAM_MIB
            data = json.dumps(m, indent=2).encode()
        zout.writestr(item, data)
os.remove(raw)
print(out)
