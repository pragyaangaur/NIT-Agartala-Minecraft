"""Gate No. 3. See smallgates.py for sources."""
import smallgates as s
NAME = "gate3"
cx, cz, axis, half, g = s.GATES[1]
CLEAR = (cx - 16, cz - 16, cx + 16, cz + 16)
def commands(gy):
    return s.gate(cx, cz, axis, half, g)
CHECKS = []
