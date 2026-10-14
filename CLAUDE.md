# Brass & Bullets: modpack repo

Lean Minecraft 1.21.1 / NeoForge 21.1.256 packwiz modpack for a private friends server. Hosted in the public
GitHub repo `Radu0120/brass-and-bullets` (since 2026-10-14; the CurseForge zip is only for a brand-new player's first
install). The two Prism instances update themselves from it at launch (see "Hosting and instance updates"). Commit
directly on the current branch (`master`), no branches, never force-push. **A request to update the pack, the instances
or the server includes pushing** (`git push origin master --tags`): the push IS what updates the instances (they pull it
at launch), so never copy jars into the instances by hand any more. Do not push otherwise, and never before the change
is tested. Both instances (Radu's and Isa's) are set up for auto-update and both launched fine from Prism (2026-10-14).
Commit author is `Radu0120` with the GitHub noreply address (set in
this repo's git config; history was rewritten once to remove a personal email). Commit trailer:
`Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

Server ops (Crafty on `DebianServer`, id `eb5ed4d2-3f4a-4eb0-9ddb-adaa800e74c5`), the update procedure, and the
pack history live in the dotfiles repo: `E:\Documents\debian_server_dotfiles\docs\NOTES.md`, "Minecraft" section.

## Layout

- `pack.toml`, `index.toml`, `mods/*.pw.toml`: packwiz metafiles (about 77 mods). `index.toml` is generated.
- `config/`: pack config defaults (Distant Horizons tuning, JEI, Xaero, FTB Quests, Open Loader packs
  `bb-tweaks` data pack and `bb-renames` client lang pack).
- `config/ftbquests/quests/`: the quest book. **Generated** (see below), do not hand-edit.
- `shaderpacks/`, `resourcepacks/`, `options.txt`: client defaults. `options.txt` is `preserve = true` in `index.toml` (installed only if absent, so players' own settings survive updates; check it stays after `packwiz refresh`). It holds the conflict-free default keybinds and enables the Mizuno cow/pig packs; edits reach new installs only. `config/xaero/minimap/default_radar_categories_client.json` is preserved the same way: root `icons` is 2 (Always) so Xaero's radar draws mob/player heads instead of dots (Xaero's default 1 = only while TAB is held). `config/xaero/world-map/profiles/default.cfg` (also preserved) sets `map_teleport_allowed = false`: no right-click "Teleport Here" on the map. Xaero only sends `/tp` chat commands, so this is cosmetic for ops (both owners are op 4); the waypoint-menu teleport toggle is per-server data (`xaero/minimap/<server>/config.txt`, `teleportationEnabled`), not shippable.
- `icon.png`: Prism instance icon (generated locally with Quartermaster/Krea 2 Turbo, keyed out of a magenta background, transparent 512 px). `export.py` puts it at the zip root; Prism uses it on a fresh import. It is in `.packwizignore`.
- `export.py`: builds the client zip. `dist/` and `*.zip` are gitignored.
- `.gitattributes` forces LF on `*.toml`, `options.txt` and `config/**`: packwiz hashes exact bytes, so CRLF
  breaks the index. `.packwizignore` keeps repo-only files (this file, `export.py`, `dist/`) out of the pack.

## Tools

- packwiz is not on PATH: `$(go env GOPATH)/bin/packwiz` (`packwiz.exe` on Windows).
- Python scripts run as `python -I -X utf8 script.py`.
- Scratch and throwaway work goes in `E:\Scratch\brass-and-bullets\<topic>\` (scratch server, jars, probes).
- Bash tool gotcha: it collapses backslashes. Use the Edit/Write tools for anything with literal `\`.

## Changing the pack

1. Edit mods/config (`packwiz add/remove/curseforge add`, or edit a `.pw.toml`).
2. `packwiz refresh`, bump `version` in `pack.toml`.
3. `python -I -X utf8 export.py` writes `dist/Brass-and-Bullets.zip`. Always use this, not
   `packwiz curseforge export` directly: the script adds `minecraft.recommendedRam = 6144` to the manifest.
   The zip name has no version on purpose (Prism names an imported instance after the zip).
4. Commit, tag `vX.Y.Z`. `git push origin master --tags` is the release (only when asked); the owner no longer needs to
   upload the zip for existing players.

## Hosting and instance updates

Pack URL: `https://raw.githubusercontent.com/Radu0120/brass-and-bullets/master/pack.toml` (raw files are cached
about 5 minutes after a push). Each Prism instance has `packwiz-installer-bootstrap.jar` in its `minecraft/` folder and
`update.cmd` (repo root, shipped in the instance zip, in `.packwizignore`) and these settings in `instance.cfg`
(`OverrideCommands=true`, `ManagedPack=false`):

    PreLaunchCommand=cmd /c .\\update.cmd

`update.cmd` runs `"%INST_JAVA%" -jar packwiz-installer-bootstrap.jar -g -s client <pack url>` and always exits 0, so a
failed update (GitHub down or rate-limited, no internet) never blocks the game. Why: on 2026-10-14 raw.githubusercontent
answered HTTP 429 once (a burst of test runs from this PC, a shared IP, or both; the limit is undocumented) and Prism
aborted the launch because the old direct command exited non-zero. Trade-off: a failed update is silent, so a client can
fall behind the server and show a version mismatch. If 429s keep coming, move the pack to GitHub Pages (new URL, new
instance zip, edit both instances). A fresh install makes about 134 raw requests; an up-to-date launch makes 2.

JVM collector: Distant Horizons prints a chat warning on every start when the JVM runs the default G1 collector. Both
instances (and the zip from `export_instance.py`) set `OverrideJavaArgs=true` and `JvmArgs=-XX:+UseZGC -XX:+ZGenerational`
in `instance.cfg` (Java 21 only; `ZGenerational` is rejected or redundant on other versions). The released
`instance-v2` zip predates this, so friends who installed it need the two lines added by hand.

**What new players get:** the GitHub release `instance-v2`
(https://github.com/Radu0120/brass-and-bullets/releases/latest), a small Prism instance zip built by
`python -I -X utf8 export_instance.py` (instance.cfg with the pre-launch command, mmc-pack.json from pack.toml,
icon, bootstrap jar, update.cmd; no mods). v1 had the fatal-on-failure command. Rebuild and attach a new release only when the loader version, RAM or pack URL
changes (`gh release create instance-vN dist/Brass-and-Bullets-instance.zip`); ordinary pack updates need no new
zip. The CurseForge zip from `export.py` is obsolete for players. NOT yet tested: importing the instance zip into a
clean Prism (the first-run Quick Setup window blocked a scripted test), so the icon key and a first launch are unverified.

**Quoting gotchas:** `instance.cfg` is a QSettings file, so a backslash in a value is an escape: write `.\\update.cmd`
(doubled, as in the line above). The `.\` prefix is needed because some PCs set `NoDefaultCurrentDirectoryInExePath=1`, where plain
`cmd /c update.cmd` fails ("not recognized"). With the old direct command, a value starting with `"` must be one quoted
string with `\"` inside, or Prism runs `javaw.exe-jar` and aborts. Edit `instance.cfg` only while that Prism is closed
(it rewrites the file from memory), or set it in Edit Instance > Settings > Custom commands. Prism does pass `INST_JAVA`
to the script (verified 2026-10-14).

So every launch compares versions and installs only what changed; removed mods are deleted; `preserve = true` files
are only written when absent. Other pack files (e.g. `config/DistantHorizons.toml`, `ftblibrary-client.snbt`,
`inventoryprofiles.json`, `xaerohud.txt`) are overwritten when the pack's copy changes, local edits to them are lost
then. Tested 2026-10-14: a fresh install is 78 mods with 0 manual prompts; on an existing instance every mod
validated and nothing was downloaded. NOT tested in Prism: launching with no internet (update.cmd is tested to exit 0 on an unreachable host).
The server is not auto-updated (needs the "nobody online, restart" routine from NOTES.md); push and server deploy
together so clients and server never differ. The jars for Woof Breeds and Whole Tree are committed in `mods/`, so a
mod release is: copy the jar, `packwiz refresh`, bump, commit, tag, push. The repo is public: no secrets, no
personal emails (commits are authored as `Radu0120` with the noreply address).

Rules learned the hard way:
- Client-only mods must be `side = "client"` (Sodium, Iris, Xaero, IPN, Mouse Tweaks, ...) or the dedicated
  server crashes on LWJGL. Server-only mods (Chunky) use `side = "server"`.
- Players must never need a manual download. CurseForge blocks third-party download for some mods (Alex's Mobs
  Continued, CodxLib), so those come from Modrinth and are bundled into the zip. All-rights-reserved mods
  cannot be bundled (Enhanced Cats was dropped for that).
- Distant Horizons is pinned to 3.3.2 (3.3.3 crashes with Chunky, DH issue #1329); its update prompt is off.
- Scorched Guns must be the "Neoforged 1.5" build (the 0.5.4 port crashes on dedicated servers).
- Test a change on the scratch server `E:\Scratch\brass-and-bullets\server` (boots in about 10 s) and not on the
  box while friends may be playing: the box has about 3 GB RAM free next to a running server.
- Cosmetic log noise to ignore: some scguns recipes, createdeco placard, create_connected
  dye-depot loot tables ("Unknown registry key"), Sable tag for copycats catwalk.

## Quest book (FTB Quests)

414 quests in 11 chapters, one dependency tree per chapter, rewards 1-30 XP levels by difficulty, progression
flexible (nothing locked). Quests are server-authoritative: a changed quest file needs a pack bump and the
update procedure from NOTES.md.

The generator is **outside the repo**: `E:/Scratch/brass-and-bullets/quests/gen.py` plus
`chapters_py/{create,farming,guns,pets,wildlife,bosses}.py` and the post-processing files
`patches, functional, links, reduce, rewards` (Scratch is disposable: if it is gone, the committed SNBT is the
only copy).

- Run: `python -I -X utf8 gen.py <outdir>`. Expect `quests: 414 chapters: 11` and `unknown ids: 0`.
- `Ch.q(key, title, icon, tasks, deps=(), xp=, lv=, desc=(), sub='', shape='')`. `lv` is XP levels 1..30
  (asserted). The first dep is the layout parent; cross-chapter deps are `(chapter, key)` tuples (real FTB
  dependencies, not drawn).
- Post-processing, in order: `patches.py` (one-off fixes), `functional.py` (`_set(ch, key, deps)` overrides so a
  link means "is a functional ingredient / teaches something new"), `links.py` (extra component links),
  `reduce.py` (transitive reduction) and `rewards.py` (`_R`: levels by the effort of that step, not by depth).
  Ubiquitous materials (cobble, planks, iron) are not linked. Guns and Storage are straight tier chains.
- **Layouts are pre-computed**: `layouts/<chapter>.json` ({key: [col,row]}, pos = cell * 1.4). When quests or
  deps change, re-run `python -I -X utf8 opt_chapter.py <chapter> [iters] [seed]` (writes
  `layouts/<ch>.seed<N>.json`; copy the best to `layouts/<ch>.json`); `gen.py` asserts the key sets match.
  `preview_html.py` writes `prev/index.html` for a look at every tab.
- **Quest ids must keep the top bit clear** (first hex digit 0-7; `hid()` in gen.py masks it). FTB Quests reads ids
  as signed longs and silently re-rolls any with the top bit set, and every dependency pointing at such a quest is
  lost, so the book loads with half its lines missing (0.1.15 shipped that way). After a deploy boot, check the
  edge count per chapter (about quests-1) instead of trusting the boot log.
- Task helpers: `I(item,n)`, `CHECK(title)`, `KILL(ent,n)`, `ADV(adv,crit)`, `STRUCT`, `DIM`, `BIOME`.
- `& ` in text is auto-escaped (FTB Quests rejects a bare `&` followed by a space).
- Kill tasks must always emit `value` (a missing value is 0 = instantly complete).
- Content decisions: Create Crafts & Additions was removed (0.1.14). Scorched Guns follows the real recipes
  (bench -> blueprint -> gun; anthralite is a plain ore; bullets gate the flintlock). Treated iron is NOT a
  prerequisite (0.1.67): the bench, press, firing unit and powered press take plain iron ingots too (checked in the
  1.5 jar's recipes); it hangs off the Macerator and only the Auto Turret quest depends on it. Exploration is the Explorer's Compass -> biome quests -> the structures that generate in that
  biome; Nether, Fortress, Stronghold and End are the gates. Structure/biome ties were verified against the jar data in 0.1.15 (the dungeons, outposts and
  trail ruins generate in many biomes, so the tied biome is a good start, not the only place). Yung's config
  disables vanilla mineshafts, so that task uses the structure tag `#bettermineshafts:better_mineshafts`. Farming groups the plantable crops into five
  quests that each track part of `farmersdelight:main/plant_all_crops`. Pets armour hangs off taming.
- Deploy a new book: in the scratch server's `config/ftbquests/quests` delete `chapters`, `lang`, `data.snbt`,
  run `gen.py` into it, boot the server once and `stop` (the mod migrates titles into `lang/en_us.snbt`), grep
  the log for `invalid item`, copy the dir into this repo, strip CR (`sed -i 's/\r$//'`), then
  `packwiz refresh`, bump, export, commit. Copy from the pack repo, not from a packwiz-installer output
  (it keeps stale quest files).

## Not verified in a real client yet

Quest text, icons, layout and task detection; per-animal `bred_all_animals` criterion tasks in Pets; the Open
Loader data pack and rename pack; Aeronautics/Sable tick cost; shaders with Iris.
