#!/bin/zsh
# Fourth pass, 8 Nov: doors, ways up, safe beds, audit, lighting, people, entity clean-up.
cd "${0:a:h}"
for grp in "library visvesvaraya newaud" "rnt" "aryabhatta" "gargi science"; do
  echo "== $grp"; python3 place.py ${=grp} 2>&1 | grep -E "commands|Exception|OutOfMemory|Unknown or|Incorrect"
done
echo "== audit fix"; python3 audit.py fix
echo "== light and life"; python3 lightlife.py | grep -v "^tile"
echo "== audit recheck"; python3 audit.py report
echo PASS4_DONE
