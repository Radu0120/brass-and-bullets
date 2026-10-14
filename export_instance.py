"""Build the Prism instance zip for new players: no mods inside, the instance updates itself from GitHub.

The zip holds a Prism/MultiMC instance (instance.cfg with the pre-launch command, mmc-pack.json with Minecraft +
NeoForge taken from pack.toml, the icon), packwiz-installer-bootstrap.jar and update.cmd (runs the installer and
always exits 0, so a GitHub outage never blocks the launch). A player imports it in Prism
(Add Instance > Import from zip) and presses Play: the first launch downloads every mod, later launches pull our pushes.
Rebuild it only when the loader version, RAM, JVM args, update.cmd or pack URL changes. The release link is shared
with players, so keep the tag instance-v2: delete the release and remake it under the same tag:
    gh release delete instance-v2 --yes
    gh release create instance-v2 dist/Brass-and-Bullets-instance.zip --latest
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

# QSettings syntax: a backslash in a value is an escape, so the file must hold a doubled one (cmd /c .\\update.cmd).
# cmd needs the .\ prefix because some PCs set NoDefaultCurrentDirectoryInExePath. The script exits 0 even when the
# installer fails, so Prism still launches the game.
pre_launch = 'cmd /c .\\\\update.cmd'
cfg = "\n".join([
    "[General]",
    "ConfigVersion=1.3",
    "InstanceType=OneSix",
    f"name={name}",
    "iconKey=brass_and_bullets",
    "AutomaticJava=true",
    "OverrideMemory=true",
    f"MaxMemAlloc={RAM_MIB}",
    # Distant Horizons warns on every start when the JVM runs the default G1 collector; Java 21 has generational ZGC.
    "OverrideJavaArgs=true",
    "JvmArgs=-XX:+UseZGC -XX:+ZGenerational",
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
    z.write(os.path.join(root, "update.cmd"), f"{name}/minecraft/update.cmd")
print(out)
