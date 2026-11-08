"""Per-building specification for the named NIT Agartala buildings.

Every value carries a provenance tag:
  M  = measured / stated in a source (OSM tag, or dimension measured in imagery)
  E  = estimated from imagery (storey count from window bands, roof from plan view)
  G  = guessed from building typology (no direct evidence)
"""
from blocks import B

# storey heights in metres
SH = 3.6

SPECS = {
 "Academic Block 1": dict(
    floors=4, storey=3.7, wall="concrete_w", wall2="concrete_lg", roof="flat",
    roof_mat="concrete_lg", win="glass_g", win_period=4, win_width=2, parapet=1,
    plinth=1, roof_kit=True, source="E", note="4 window bands counted in Esri imagery; long 34x66 m slab, long axis N-S"),
 "Academic Block 2": dict(
    floors=3, storey=3.7, wall="concrete_w", wall2="concrete_lg", roof="flat",
    roof_mat="concrete_lg", win="glass_g", win_period=3, win_width=2, parapet=1,
    plinth=1, rooflight=True, source="E", note="3 window bands; O-shaped plan with inner court visible in imagery"),
 "Library": dict(
    floors=3, storey=3.9, wall="concrete_w", wall2="concrete_w", roof="drum",
    roof_mat="deepslate_t", roof_mat2="concrete_lg", win="glass_lb", win_period=3, win_width=2, parapet=1,
    plinth=2, drum=True, source="E", note="octagonal plan; central raised drum visible as a bright disc in imagery"),
 "CSE Department": dict(
    floors=4, storey=3.8, wall="concrete_lg", wall2="concrete_w", roof="flat",
    roof_mat="concrete_lg", win="glass_b", win_period=3, win_width=2, parapet=1,
    plinth=1, roof_kit=True, source="E", note="OSM height 15.20 m -> 4 storeys"),
 "ECE Building": dict(
    floors=7, storey=3.4, wall="concrete_w", wall2="concrete_lg", roof="gable_low",
    roof_mat="concrete_lg", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="M", note="OSM building:levels=7 (unverified); long 78x28 m slab"),
 "Civil Building": dict(
    floors=5, storey=4.0, wall="concrete_lg", wall2="concrete_w", roof="flat",
    roof_mat="concrete_lg", win="glass_g", win_period=3, win_width=2, parapet=1,
    plinth=1, roof_kit=True, source="M", note="OSM height=20 m -> 5 storeys"),
 "Chemical Department": dict(
    floors=2, storey=3.8, wall="concrete_w", wall2="concrete_g", roof="flat",
    roof_mat="concrete_lg", win="glass_g", win_period=3, win_width=2, parapet=1,
    plinth=1, source="E", note="2 storeys per two independent researchers; 33rd BWC places some Chemical rooms in a separate new academic building"),
 "Arybhatta Hostel": dict(
    floors=3, storey=3.4, wall="concrete_w", wall2="terracotta_w", roof="gable",
    roof_mat="terracotta_r", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="M", note="OSM building:levels=3; U-shaped plan, pitched red-tile roofs in imagery"),
 "Gargi Girls Hostel": dict(
    floors=3, storey=3.4, wall="concrete_w", wall2="terracotta_w", roof="gable",
    roof_mat="terracotta_r", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="E", note="OSM levels=15 rejected as implausible (a 15-storey block is 52 m); 3 bands in imagery"),
 "RNT Mess": dict(
    floors=2, storey=4.6, wall="concrete_w", wall2="concrete_lg", roof="flat",
    roof_mat="concrete_lg", win="glass_lg", win_period=3, win_width=2, parapet=1,
    plinth=1, source="M", note="OSM height=15 m over a 97x52 m curved plan; 2 tall storeys"),
 "Visvesvaraya Auditorium": dict(
    floors=1, storey=11.0, wall="concrete_w", wall2="terracotta_w", roof="hip",
    roof_mat="terracotta_r", win="glass_br", win_period=4, win_width=2, parapet=0,
    plinth=2, portico=True, source="M", note="OSM height=12 m; single tall hall volume with a balcony, deep roof, portico on the road side"),
 "New Auditorium": dict(
    floors=1, storey=13.0, wall="concrete_lg", wall2="concrete_g", roof="shell",
    roof_mat="concrete_gr", win="glass_c", win_period=5, win_width=3, parapet=0,
    plinth=2, source="M", note="OSM height=15 m; large-span shell roof, green in imagery"),
 "NITA Hospital": dict(
    floors=2, storey=4.0, wall="concrete_w", wall2="concrete_lg", roof="flat",
    roof_mat="concrete_lg", win="glass_lb", win_period=3, win_width=2, parapet=1,
    plinth=1, source="E", note="2 window bands in imagery"),
 "Guest House": dict(
    floors=3, storey=3.4, wall="concrete_w", wall2="terracotta_w", roof="hip",
    roof_mat="terracotta_r", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="E", note="3 bands; low hip roof with red tiles in imagery"),
 "Shopping Complex": dict(
    floors=2, storey=4.0, wall="concrete_w", wall2="terracotta", roof="radial",
    roof_mat="terracotta_r", win="glass_br", win_period=4, win_width=2, parapet=1,
    plinth=1, source="M", note="OSM height=12 m; circular market with radial roof segments and a ring arcade"),
 "CSE Canteen": dict(
    floors=1, storey=4.2, wall="concrete_w", wall2="concrete_lg", roof="shed",
    roof_mat="concrete_g", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="E", note="single-storey canteen shed"),
 "ECE Canteen": dict(
    floors=1, storey=4.0, wall="concrete_w", wall2="concrete_lg", roof="flat",
    roof_mat="concrete_g", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="E", note="single-storey canteen"),
 "Monty Xerox": dict(
    floors=2, storey=3.3, wall="concrete_lg", wall2="concrete_w", roof="flat",
    roof_mat="concrete_g", win="glass_g", win_period=3, win_width=2, parapet=0,
    plinth=1, source="M", note="OSM building:levels=2"),
 "NIT Agartala": dict(
    floors=3, storey=4.0, wall="concrete_w", wall2="brick", roof="gable",
    roof_mat="terracotta_r", win="glass_br", win_period=3, win_width=2, parapet=0,
    plinth=1, source="E", note="main academic cluster; 3 storeys (ESTIMATED from footprint and imagery); parallel wings with pitched red roofs"),
 "Mechanical Department": dict(
    floors=2, storey=5.4, wall="concrete_lg", wall2="concrete_g", roof="flat",
    roof_mat="concrete_lg", win="glass_g", win_period=4, win_width=2, parapet=1,
    plinth=1, roof_kit=True, source="E", note="4631 m2 footprint, the largest named building; workshop-scale storey heights"),
 "Science Block": dict(
    floors=3, storey=3.7, wall="concrete_w", wall2="concrete_lg", roof="flat",
    roof_mat="concrete_lg", win="glass_g", win_period=3, win_width=2, parapet=1,
    plinth=1, roof_kit=True, source="E", note="3 window bands in imagery"),
}

# default spec for the un-named footprint set
DEFAULT = dict(floors=2, storey=3.4, wall="concrete_w", wall2="concrete_lg", roof="flat",
               roof_mat="concrete_lg", win="glass_g", win_period=3, win_width=2, parapet=1,
               plinth=1, source="G", note="generic campus style")

# named buildings whose OSM footprint is a multipolygon relation or needs merging
ALIASES = {"Arybhatta Hostel": "Aryabhatta Hostel", "Mechanical Department": "Mechanical Department"}
# OSM spells it "Arybhatta"; accept both spellings
SPECS.setdefault("Aryabhatta Hostel", SPECS["Arybhatta Hostel"])
