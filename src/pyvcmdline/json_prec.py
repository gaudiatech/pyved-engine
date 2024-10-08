"""
this file is designed to store many metadat.json precursors
(str-typed Const. that will be used to init game bundles ...)
"""


JSON_PREC_GAMEZERO = """\
{
"vmlib_ver":"void",
"dependencies":{
},
"description":"this is a placeholder so you can describe your game",
"author":"placeholder_author",
"asset_list": ["lion.png"],
"asset_base_folder": "my_folder",
"sound_base_folder":".",
"sound_list": [
],
"slug": "foundation_Cartridge",
"title": "Untitled Game",
"thumbnail512x384": "thumb_2.png",
"thumbnail512x512": "thumb_1.png",
"ktg_services": false,
"instructions": "not provided",
"uses_challenge": false,
"has_game_server": false,
"ncr_faucet": false,
"game_genre": ["Experimental"]
}
"""

JSON_PREC_PLATFORMER = """\
{
"vmlib_ver":"void",
"dependencies":{
},
"description": "this is an example of platformer",
"author": "KataGames_Team",
"asset_list": [
"my_map.ncsv"
],
"asset_base_folder":".",
"sound_base_folder":".",
"sound_list": [],
"slug": "pyvTutoZero",
"title": "Skeleton for a platformer game",
"build_date": "Thu Sep 14 11:31:49 2023",
"thumbnail512x384": "thumb_2.png",
"thumbnail512x512": "thumb_1.png",
"ktg_services": false,
"instructions": "not provided",
"uses_challenge": false,
"has_game_server": false,
"ncr_faucet": false,
"game_genre": ["Platformer"]
}
"""

JSON_PREC_CHESS ="""\
{
"vmlib_ver":"void",
"dependencies":{
},
"description": "this is a placeholder so you can describe your game",
"author": "moonbak et al.",
"asset_base_folder":".",
"sound_base_folder":".",
"asset_list": [
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
"sound_list": [],
"slug": "testChess",
"title": "chessBundle",
"instructions": "no instructions provided.",
"build_date": "Fri Sep 15 15:10:47 2023",
"thumbnail512x384": "thumb_2.png",
"thumbnail512x512": "thumb_1.png",
"ktg_services": false,
"instructions": "not provided",
"uses_challenge": false,
"has_game_server": false,
"ncr_faucet": false,
"game_genre": ["Classics"]
}
"""

JSON_PREC_ROGUE = """
{
"vmlib_ver":"void",
"dependencies":{
},
  "description": "a basic demo for a roguelike game",
  "author": "thomas",
  "asset_base_folder": ".",
  "sound_base_folder": ".",
  "asset_list": [
    "smallninja_sprites.json",
    "tileset.png",
    "monster.png",
    "avatar1.png"
  ],
  "sound_list": [],
  "slug": "JeuEvolue",
  "title": "Roguelike Template",
  "build_date": "Tue Sep 17 09:06:21 2024",
  "thumbnail512x384": "thumb_2.png",
  "thumbnail512x512": "thumb_1.png",
  "ktg_services": false,
  "instructions": "no instructions provided",
  "uses_challenge": false,
  "has_game_server": false,
  "ncr_faucet": false,
  "game_genre": [
    "Roguelike"
  ],
  "game_title": "JeuEvolue",
  "source_files": [
    "gamedef.py",
    "glvars.py",
    "mvc_parts.py",
    "__init__.py"
  ]
}
"""

TEMPL_ID_TO_JSON_STR = {
    0: JSON_PREC_GAMEZERO,
    1: JSON_PREC_GAMEZERO,
    2: JSON_PREC_PLATFORMER,
    3: JSON_PREC_CHESS,
    4: JSON_PREC_ROGUE
}
