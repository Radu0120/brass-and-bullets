"""Build the Prism instance zip for new players: no mods inside, the instance updates itself from GitHub.

The zip holds a Prism/MultiMC instance (instance.cfg with the packwiz pre-launch command, mmc-pack.json with
Minecraft + NeoForge taken from pack.toml, the icon) and packwiz-installer-bootstrap.jar. A player imports it in Prism
(Add Instance > Import from zip) and presses Play: the first launch downloads every mod, later launches pull our pushes.
Rebuild it only when the loader version, RAM or pack URL changes. Attach it to a GitHub release:
    gh release create instance-vN dist/Brass-and-Bullets-instance.zip
Usage: python export_instance.py   ->  dist/<name>-instance.zip
"""
import json, os, re, urllib.request, zipfile

RAM_MIB = 6144
PACK_URL = "https://raw.githubusercontent.com/Radu0120/brass-and-bullets/master/pack.toml"
BOOTSTRAP_URL = "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar"

root = os.path.dirname(os.path.abspath(__file__))
pack = open(os.path.join(root, "pack.toml"), encoding="utf-8").read()
name = re.search(r'^name = "(.*)"', pack, re.M).group(1).replace(" & ", "-and-").replace(" ", "-")
minecraft = re.search(r'^minecraft = "(.*)"', pack, re.M).group(1)
neoforge = re.search(r'^neoforge = "(.*)"', pack, re.M).group(1)
dist = os.path.join(root, "dist")
os.makedirs(dist, exist_ok=True)
out = os.path.join(dist, f"{name}-instance.zip")

jar = os.path.join(dist, "packwiz-installer-bootstrap.jar")
if not os.path.exists(jar):
    req = urllib.request.Request(BOOTSTRAP_URL, headers={"User-Agent": "brass-and-bullets-export"})
    with urllib.request.urlopen(req) as r, open(jar, "wb") as f:
        f.write(r.read())

# QSettings syntax: a value starting with a quote must be one quoted string with \" inside, or Prism strips the
# quotes and runs "javaw.exe-jar". -g = no GUI, -s client = client-side mods only.
pre_launch = '"\\"$INST_JAVA\\" -jar packwiz-installer-bootstrap.jar -g -s client ' + PACK_URL + '"'
cfg = "\n".join([
    "[General]",
    "ConfigVersion=1.3",
    "InstanceType=OneSix",
    f"name={name}",
    "iconKey=brass_and_bullets",
    "AutomaticJava=true",
    "OverrideMemory=true",
    f"MaxMemAlloc={RAM_MIB}",
    "OverrideCommands=true",
    f"PreLaunchCommand={pre_launch}",
    "",
])
components = {"formatVersion": 1, "components": [
    {"uid": "net.minecraft", "version": minecraft, "important": True},
    {"uid": "net.neoforged", "version": neoforge},
]}

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr(f"{name}/instance.cfg", cfg)
    z.writestr(f"{name}/mmc-pack.json", json.dumps(components, indent=4))
    z.write(os.path.join(root, "icon.png"), f"{name}/icon.png")
    z.write(jar, f"{name}/minecraft/packwiz-installer-bootstrap.jar")
print(out)
