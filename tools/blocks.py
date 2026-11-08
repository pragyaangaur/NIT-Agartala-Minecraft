"""Block palette and small helpers.  Index 0 is always air."""
import numpy as np

# (name, properties) in palette order; index 0 = air
PALETTE = [
    ("minecraft:air", {}),
]
_idx = {"minecraft:air|": 0}

def bid(name, **props):
    key = name + "|" + ",".join(f"{k}={v}" for k, v in sorted(props.items()))
    if key in _idx:
        return _idx[key]
    PALETTE.append((name, props))
    _idx[key] = len(PALETTE) - 1
    if len(PALETTE) > 60000:
        raise RuntimeError("palette overflow")
    return _idx[key]

AIR = 0

def _add():
    b = {}
    def g(name, **props): return bid(name, **props)
    # ground / natural
    b['stone']       = g("minecraft:stone")
    b['deepslate']   = g("minecraft:deepslate")
    b['dirt']        = g("minecraft:dirt")
    b['grass']       = g("minecraft:grass_block", snowy="false")
    b['coarse']      = g("minecraft:coarse_dirt")
    b['podzol']      = g("minecraft:podzol", snowy="false")
    b['sand']        = g("minecraft:sand")
    b['gravel']      = g("minecraft:gravel")
    b['clay']        = g("minecraft:clay")
    b['mud']         = g("minecraft:mud")
    b['packed_mud']  = g("minecraft:packed_mud")
    b['water']       = g("minecraft:water", level="0")
    b['red_sand']    = g("minecraft:red_sand")
    b['moss']        = g("minecraft:moss_block")
    b['rooted']      = g("minecraft:rooted_dirt")
    b['tallgrass']   = g("minecraft:short_grass")
    b['fern']        = g("minecraft:fern")
    b['flower_r']    = g("minecraft:poppy")
    b['flower_y']    = g("minecraft:dandelion")
    # foliage
    b['oak_leaves']     = g("minecraft:oak_leaves", persistent="false", distance="1", waterlogged="false")
    b['dark_leaves']    = g("minecraft:dark_oak_leaves", persistent="false", distance="1", waterlogged="false")
    b['jungle_leaves']  = g("minecraft:jungle_leaves", persistent="false", distance="1", waterlogged="false")
    b['birch_leaves']   = g("minecraft:birch_leaves", persistent="false", distance="1", waterlogged="false")
    b['oak_log']        = g("minecraft:oak_log", axis="y")
    b['dark_log']       = g("minecraft:dark_oak_log", axis="y")
    b['jungle_log']     = g("minecraft:jungle_log", axis="y")
    # masonry / concrete
    b['concrete_w']     = g("minecraft:white_concrete")
    b['concrete_lg']    = g("minecraft:light_gray_concrete")
    b['concrete_g']     = g("minecraft:gray_concrete")
    b['concrete_b']     = g("minecraft:black_concrete")
    b['concrete_r']     = g("minecraft:red_concrete")
    b['concrete_o']     = g("minecraft:orange_concrete")
    b['concrete_y']     = g("minecraft:yellow_concrete")
    b['concrete_l']     = g("minecraft:lime_concrete")
    b['concrete_c']     = g("minecraft:cyan_concrete")
    b['concrete_lb']    = g("minecraft:light_blue_concrete")
    b['concrete_br']    = g("minecraft:brown_concrete")
    b['concrete_p']     = g("minecraft:pink_concrete")
    b['concrete_m']     = g("minecraft:magenta_concrete")
    b['concrete_pu']    = g("minecraft:purple_concrete")
    b['concrete_bg']    = g("minecraft:blue_concrete")
    b['concrete_gr']    = g("minecraft:green_concrete")
    b['terracotta']     = g("minecraft:terracotta")
    b['terracotta_w']   = g("minecraft:white_terracotta")
    b['terracotta_lg']  = g("minecraft:light_gray_terracotta")
    b['terracotta_g']   = g("minecraft:gray_terracotta")
    b['terracotta_b']   = g("minecraft:black_terracotta")
    b['terracotta_r']   = g("minecraft:red_terracotta")
    b['terracotta_o']   = g("minecraft:orange_terracotta")
    b['terracotta_br']  = g("minecraft:brown_terracotta")
    b['brick']          = g("minecraft:bricks")
    b['stone_brick']    = g("minecraft:stone_bricks")
    b['mossy_brick']    = g("minecraft:mossy_stone_bricks")
    b['chiselled']      = g("minecraft:chiseled_stone_bricks")
    b['smooth_stone']   = g("minecraft:smooth_stone")
    b['stone_slab_top'] = g("minecraft:smooth_stone_slab", type="top", waterlogged="false")
    b['andesite']       = g("minecraft:andesite")
    b['pol_andesite']   = g("minecraft:polished_andesite")
    b['diorite']        = g("minecraft:diorite")
    b['pol_diorite']    = g("minecraft:polished_diorite")
    b['granite']        = g("minecraft:granite")
    b['pol_granite']    = g("minecraft:polished_granite")
    b['cobble']         = g("minecraft:cobblestone")
    b['mossy_cobble']   = g("minecraft:mossy_cobblestone")
    b['sandstone']      = g("minecraft:sandstone")
    b['cut_sandstone']  = g("minecraft:cut_sandstone")
    b['quartz']         = g("minecraft:quartz_block")
    b['smooth_quartz']  = g("minecraft:smooth_quartz")
    b['deepslate_t']    = g("minecraft:deepslate_tiles")
    b['blackstone']     = g("minecraft:polished_blackstone")
    b['iron']           = g("minecraft:iron_block")
    b['iron_bars']      = g("minecraft:iron_bars", east="true", north="true", south="true", waterlogged="false", west="true")
    b['copper']         = g("minecraft:copper_block")
    b['tuff']           = g("minecraft:tuff")
    b['calcite']        = g("minecraft:calcite")
    # glass
    b['glass']      = g("minecraft:glass")
    b['glass_w']    = g("minecraft:white_stained_glass")
    b['glass_lg']   = g("minecraft:light_gray_stained_glass")
    b['glass_g']    = g("minecraft:gray_stained_glass")
    b['glass_b']    = g("minecraft:black_stained_glass")
    b['glass_br']   = g("minecraft:brown_stained_glass")
    b['glass_c']    = g("minecraft:cyan_stained_glass")
    b['glass_lb']   = g("minecraft:light_blue_stained_glass")
    b['glass_gr']   = g("minecraft:green_stained_glass")
    b['glass_bl']   = g("minecraft:blue_stained_glass")
    b['glass_r']    = g("minecraft:red_stained_glass")
    # wood
    b['planks']       = g("minecraft:oak_planks")
    b['planks_dk']    = g("minecraft:dark_oak_planks")
    b['planks_sp']    = g("minecraft:spruce_planks")
    b['planks_bi']    = g("minecraft:birch_planks")
    b['spruce_log']   = g("minecraft:spruce_log", axis="y")
    b['oak_fence']    = g("minecraft:oak_fence", east="true", north="true", south="true", waterlogged="false", west="true")
    b['wire']         = g("minecraft:white_wool")
    # slabs / stairs helpers handled in geometry
    b['slab_bottom']  = g("minecraft:smooth_stone_slab", type="bottom", waterlogged="false")
    b['stair_n'] = g("minecraft:stone_brick_stairs", facing="north", half="bottom", shape="straight", waterlogged="false")
    b['stair_s'] = g("minecraft:stone_brick_stairs", facing="south", half="bottom", shape="straight", waterlogged="false")
    b['stair_e'] = g("minecraft:stone_brick_stairs", facing="east", half="bottom", shape="straight", waterlogged="false")
    b['stair_w'] = g("minecraft:stone_brick_stairs", facing="west", half="bottom", shape="straight", waterlogged="false")
    b['wall']     = g("minecraft:cobblestone_wall", east="none", north="none", south="none", up="true", waterlogged="false", west="none")
    return b

B = _add()

def palette_list():
    """Sponge/MC palette as list of dicts."""
    out = []
    for name, props in PALETTE:
        d = {"Name": nbt_str(name)}
        if props:
            d["Properties"] = {k: nbt_str(v) for k, v in props.items()}
        out.append(d)
    return out

class nbt_str(str):
    pass
