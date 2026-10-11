# Brass & Bullets: modpack repo

Lean Minecraft 1.21.1 / NeoForge 21.1.256 packwiz modpack for a private friends server. Distributed as a plain
zip the owner uploads by hand: **no GitHub repo, no CurseForge project. Never push or create remotes.** Commit
locally only when asked; commit directly on `main`, no branches. Commit trailer:
`Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

Server ops (Crafty on `DebianServer`, id `eb5ed4d2-3f4a-4eb0-9ddb-adaa800e74c5`), the update procedure, and the
pack history live in the dotfiles repo: `E:\Documents\debian_server_dotfiles\docs\NOTES.md`, "Minecraft" section.

## Layout

- `pack.toml`, `index.toml`, `mods/*.pw.toml`: packwiz metafiles (about 69 mods). `index.toml` is generated.
- `config/`: pack config defaults (Distant Horizons tuning, JEI, Xaero, FTB Quests, Open Loader packs
  `bb-tweaks` data pack and `bb-renames` client lang pack).
- `config/ftbquests/quests/`: the quest book. **Generated** (see below), do not hand-edit.
- `shaderpacks/`, `options.txt`: client defaults.
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
4. Commit, tag `vX.Y.Z`. The owner uploads the zip.

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

412 quests in 11 chapters, one dependency tree per chapter, rewards 1-30 XP levels by difficulty, progression
flexible (nothing locked). Quests are server-authoritative: a changed quest file needs a pack bump and the
update procedure from NOTES.md.

The generator is **outside the repo**: `E:/Scratch/brass-and-bullets/quests/gen.py` plus
`chapters_py/{create,farming,guns,pets,wildlife,bosses}.py` and the post-processing files
`patches, functional, links, reduce, rewards` (Scratch is disposable: if it is gone, the committed SNBT is the
only copy).

- Run: `python -I -X utf8 gen.py <outdir>`. Expect `quests: 412 chapters: 11` and `unknown ids: 0`.
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
  (macerator -> treated iron -> bench -> blueprint -> gun; anthralite is a plain ore; bullets gate the
  flintlock). Exploration is the Explorer's Compass -> biome quests -> the structures that generate in that
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
