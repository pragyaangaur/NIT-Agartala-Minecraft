#!/bin/zsh
# Third pass, 7 Nov night: detail, interiors, leaf fix. Each group is its own server session.
cd "${0:a:h}"
for grp in "library visvesvaraya newaud" "rnt" "aryabhatta" "gargi science" "civil mechanical chemical hospital" "foodcourt bungalow kv market guesthouse" "sports"; do
  echo "== $grp"; python3 place.py ${=grp} 2>&1 | grep -E "commands|Exception|OutOfMemory|Unknown or|Incorrect"
done
echo "== nightlights"
python3 - <<'PY'
import nightlights, place
from mcserver import run, write_functions, forceload_cmds
nl = []
for n, (b, c) in enumerate(nightlights.all_commands()):
    if c:
        ids = write_functions(place.WORLD, f"nl_{n}", c)
        nl += forceload_cmds(*b) + ["function " + f for f in ids] + ["forceload remove all"]
log = run(place.WORLD, nl, wait_load=4)
print("night lights done", [l for l in log.splitlines() if "Exception" in l][:3])
PY
echo "== leaves"
python3 leaves.py
echo PASS3_DONE
