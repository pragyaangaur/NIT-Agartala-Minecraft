# Contributing to NIT Agartala in Minecraft

Anyone who knows the campus can help, and you do not need to be a programmer. The map is large, so the best way in is to pick one small piece, such as a single building, one hostel's rooms or a stretch of road, and make it better. This guide lists the open jobs, explains the three ways to help, and shows how to get an AI agent to do the technical part for you.

## Contents

1. [Ways to help](#ways-to-help)
2. [Pick a job](#pick-a-job)
3. [Using an AI agent](#using-an-ai-agent)
4. [Setting up](#setting-up)
5. [Making a change yourself](#making-a-change-yourself)
6. [Sending your change](#sending-your-change)
7. [House rules](#house-rules)

## Ways to help

**Without any code.** Play the map and [open an issue](../../issues/new/choose) when something looks wrong, such as a floating block, a missing door or a building in the wrong colour. Give the coordinates (press <kbd>F3</kbd> and read the XYZ line) and a screenshot. You can also open an issue with photos or notes about a building you know, especially what its rooms look like inside. Someone else can then turn that into a change.

**With an AI agent.** Tools such as Claude Code, Codex, Cursor or GitHub Copilot can read this repository, write the script for you, run it and check the result. You describe the change in plain words and check the result in the game. The [Using an AI agent](#using-an-ai-agent) section has a prompt you can copy.

**By writing code yourself.** Every building is one Python script in `tools/hand/`, so you can change one place without touching the rest. The [Making a change yourself](#making-a-change-yourself) section explains how.

## Pick a job

Choose one item, say in an issue that you are working on it so two people do not do the same thing, and keep the change small.

### Interiors (the biggest gap)

The furniture inside almost every building was placed by a script and is only a placeholder. It does not show what the real rooms look like. If you have been inside a building, you can make it real.

| Job | Where | Size |
| --- | --- | --- |
| Real room layout for one RNT or Aryabhatta hostel block | `rnt.py`, `aryabhatta.py`, `interiors.py` | Medium |
| The real Aryabhatta mess (where it is and what it looks like) | `aryabhatta.py` | Medium |
| RNT Dining Hall counters, tables and wash area | `rnt.py`, `interiors.py` | Small |
| Classrooms and labs in one department building | the department's script | Medium |
| The Library's real floor plan and reading areas | `library.py` | Medium |
| Stage, seating and foyer of either auditorium | `newaud.py`, `visvesvaraya.py` | Small |
| Proper staircases in place of ladders in one building | that building's script | Small |

### Buildings that still need references

| Job | Notes | Size |
| --- | --- | --- |
| Dhalai, Gomati, Howrah and Saima hostels | Positions are known only roughly | Large |
| Faculty Quarters | Seen in the tour videos but not found on the map yet | Medium |
| The west academic cluster | New Academic Building, CDAC, Maths, the workshops, the Smart Lecture Halls and others | Large |
| Bio Engineering, and the New Canteen and VCR building | Next to the Library | Medium |
| Name and style any unnamed building you recognise | See `docs/BUILDINGS.md` for what is done | Small |

### Outdoors and details

| Job | Size |
| --- | --- |
| Name signs on department buildings and hostels | Small |
| Real tree lines, gardens and the plants you remember | Small |
| Shops and stalls in the market and near the gates | Medium |
| Glitches: floating blocks, missing doors, dark rooms | Small |

### Things to build with the map

You do not have to change the map itself. Treasure hunt maps, campus tour routes, a minigame or a festival layout made in your own copy are welcome as separate folders under `extras/`. Explain in a README how to play them.

## Using an AI agent

An agent works best with a narrow job and a clear way to check it. Start your agent in the repository folder and give it something like the prompt below. Change the first line to your job.

```text
I want to improve the RNT Dining Hall interior in this Minecraft map of NIT Agartala.
Read README.md, CONTRIBUTING.md and docs/HOW_IT_WORKS.md first.
Here is what the real hall looks like: <describe it, or attach photos>.

Rules:
- Only change the scripts for this building (and interiors.py if you must).
- Put the world in work/world_edit/ as described in CONTRIBUTING.md before running anything.
- Place the building with `python3 place.py <name>` from tools/hand/.
- Run `python3 audit.py report` afterwards. It must report 0 problems.
  If it does not, run `python3 audit.py fix` and report again.
- Render the area with render_readme.py so I can look at it, and tell me the
  /tp command to see it in the game.
- Explain what you changed in plain words before you commit.
```

After the agent finishes, open the world in Minecraft and walk through what it built. You are responsible for what goes into your pull request, so read what the agent says it changed. If something looks wrong, tell the agent what you saw and ask it to fix it.

## Setting up

You need these four things.

1. **Minecraft Java Edition 26.3 or newer.**
2. **Python 3.10 or newer.** Then install the libraries from the repository folder:

   ```bash
   pip install -r requirements.txt
   ```

3. **Java 25 or newer** to run the Minecraft server headless. On macOS the Minecraft launcher already includes one and the scripts find it. Elsewhere, install Java 25, or set `NITA_JAVA` to the full path of the `java` program.
4. **The world in the right place.** Download the world zip from the [latest release](../../releases/latest), unzip it, and rename the folder so that this file exists:

   ```text
   work/world_edit/level.dat
   ```

Then get the code:

```bash
git clone https://github.com/pragyaangaur/NIT-Agartala-Minecraft.git
cd NIT-Agartala-Minecraft
```

If you have not used GitHub before, click **Fork** at the top of the repository page first, and clone your fork instead. You will send your change from there.

## Making a change yourself

[docs/BUILDINGS.md](docs/BUILDINGS.md) lists every named building with its script and a teleport command. Open the script and read its docstring, which says where each detail came from.

There are two kinds of building scripts.

- **Voxel modules** such as `ece.py` and `library.py` draw the building block by block in a small grid with `v.box(...)` and `v.set(...)`. They suit buildings with a lot of hand detail.
- **Footprint modules** such as `civil.py` and `rnt.py` raise the building from its real outline with `extrude.Building(...)`, and `interiors.py` adds rooms to them.

To place a building and check it:

```bash
cd tools/hand
python3 place.py library          # writes the building into work/world_edit
python3 audit.py report           # must print 0 {}
python3 render_readme.py ../../work/world_edit /tmp/look iso library
```

The first run downloads the official server jar. `place.py` prints any command the server rejected, so read the last lines of its output. To look at your change in the game, copy `work/world_edit` into your `saves` folder under a new name and open it.

For a new building, copy the closest existing script, give it a new name, and set `CLEAR` to the box it is allowed to clear. Write the source of every detail in the docstring, such as a video timestamp, a photo you took or a map label.

## Sending your change

1. Make a branch: `git checkout -b dining-hall-interior`.
2. Commit only the scripts and docs you changed. Never commit world files, renders, videos or anything in `work/`. The `.gitignore` already keeps most of them out.
3. Push to your fork and open a pull request. Say what you changed and where it is (the `/tp` command). Name your source and add one screenshot from the game. Also paste the line from `audit.py report` showing 0 problems.

Small pull requests are reviewed fastest. One building or one fix per pull request is ideal.

## House rules

- **Be accurate where you can and honest where you cannot.** If a detail is a guess, say so in the docstring.
- **Keep it about the campus.** No real names of students or staff on signs, and no private or personal information.
- **Respect other people's work.** Do not overwrite a building someone else is working on. Ask in their issue first.
- **Credit your sources.** Only use photos and videos you are allowed to use, and link to them rather than adding them to the repository.

By contributing you agree that your contribution is released under the [MIT License](LICENSE) of this project.
