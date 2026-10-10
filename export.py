"""Build the client zip: packwiz CurseForge export + recommendedRam in manifest.json.

packwiz can't write minecraft.recommendedRam. Prism and the CurseForge app set the
instance's max memory from it on a fresh import (Prism clamps it to 90% of system RAM).
Also adds icon.png (repo root, not in the pack index) as the Prism instance icon.
Usage: python export.py   ->  dist/<name>.zip
No version in the filename: Prism names a local import after the zip file, and the version
is already in the manifest (Prism shows it as the pack version).
"""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile

RAM_MIB = 6144

root = os.path.dirname(os.path.abspath(__file__))
pack = open(os.path.join(root, "pack.toml"), encoding="utf-8").read()
name = re.search(r'^name = "(.*)"', pack, re.M).group(1).replace(" & ", "-and-").replace(" ", "-")
out = os.path.join(root, "dist", f"{name}.zip")
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
    # Prism picks up icon.png at the zip root as the instance icon on a fresh import
    zout.write(os.path.join(root, "icon.png"), "icon.png")
os.remove(raw)
print(out)
