"""
this file is designed to store many metadat.json precursors
(str-typed Const. that will be used to init game bundles ...)
"""


JSON_PREC_NOASSETS = """\
{
"vmlib_ver":"void",
"dependencies":{
    "pyved_engine": "???"
},
"description":"this is a placeholder so you can describe your game",
"author":"placeholder_author",
"assets":[
],
"sounds": [
],
"slug": "foundation_Cartridge",
"title": "Untitled Game",
"thumbnail512x384": "thumb_2.png",
"thumbnail512x512": "thumb_1.png",
"ktg_services": false,
"instructions": "not provided"
}
"""

JSON_PREC_PLATFORMER = """\
{
"vmlib_ver": "23_9a1",
"dependencies": {
"pyved_engine": "???"
},
"description": "this is an example of platformer",
"author": "KataGames_Team",
"assets": [
"my_map.ncsv"
],
"sounds": [],
"slug": "pyvTutoZero",
"title": "Skeleton for a platformer game",
"build_date": "Thu Sep 14 11:31:49 2023",
"thumbnail512x384": "thumb_2.png",
"thumbnail512x512": "thumb_1.png",
"ktg_services": false,
"instructions": "not provided"
}
"""

JSON_PREC_CHESS ="""
{
"vmlib_ver": "23_9a1",
"dependencies": {
"pyved_engine": "???"
},
"description": "this is a placeholder so you can describe your game",
"author": "moonbak et al.",
"assets": [
"black_bishop.png",
"black_king.png",
"black_knight.png",
"black_pawn.png",
"black_queen.png",
"black_rook.png",
"white_bishop.png",
"white_king.png",
"white_knight.png",
"white_pawn.png",
"white_queen.png",
"white_rook.png",
"white_square.png",
"brown_square.png",
"cyan_square.png"
],
"sounds": [],
"slug": "testChess",
"title": "chessBundle",
"instructions": "no instructions provided.",
"build_date": "Fri Sep 15 15:10:47 2023",
"thumbnail512x384": "thumb_2.png",
"thumbnail512x512": "thumb_1.png",
"ktg_services": false,
"instructions": "not provided"
}
"""

JSON_PREC_ROGUE = """
{
    "vmlib_ver": "24_3a1",
    "dependencies": {
        "pyved_engine": "???"
    },
    "description": "a basic demo for a roguelike game",
    "author": "moonbak",
    "assets": [
        "smallninja_sprites.json",
        "tileset.png",
        "monster.png",
        "avatar1.png"
    ],
    "sounds": [],
    "slug": "roguelikeDemo",
    "title": "Roguelike Template",
    "build_date": "Tue Apr  2 15:40:11 2024",
    "thumbnail512x384": "thumb_2.png",
    "thumbnail512x512": "thumb_1.png",
    "ktg_services": false,
    "instructions": "no instructions provided",
    "game_title": "Untitled Roguelike"
}
"""

TEMPL_ID_TO_JSON_STR = {
    0: JSON_PREC_NOASSETS,
    1: JSON_PREC_NOASSETS,
    2: JSON_PREC_PLATFORMER,
    3: JSON_PREC_CHESS,
    4: JSON_PREC_ROGUE
}
