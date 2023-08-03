import pyved_engine as pyv


images = dict()


def load_img(assetname):
    return pyv.pygame.image.load('images/' + assetname)


def preload_assets():
    global images
    square_size = 100
    pyg = pyv.pygame

    images['white_square'] = load_img("white_square.png")
    images['brown_square'] = load_img("brown_square.png")
    images['cyan_square'] = load_img("cyan_square.png")

    black_pawn = load_img("Chess_tile_pd.png")
    images['black_pawn'] = pyg.transform.scale(black_pawn, (square_size, square_size))

    black_rook = load_img("Chess_tile_rd.png")
    images['black_rook'] = pyg.transform.scale(black_rook, (square_size, square_size))

    black_knight = load_img("Chess_tile_nd.png")
    images['black_knight'] = pyg.transform.scale(black_knight, (square_size, square_size))

    black_bishop = load_img("Chess_tile_bd.png")
    images['black_bishop'] = pyg.transform.scale(black_bishop, (square_size, square_size))

    black_king = load_img("Chess_tile_kd.png")
    images['black_king'] = pyg.transform.scale(black_king, (square_size, square_size))

    black_queen = load_img("Chess_tile_qd.png")
    images['black_queen'] = pyg.transform.scale(black_queen, (square_size, square_size))

    white_pawn = load_img("Chess_tile_pl.png")
    images['white_pawn'] = pyg.transform.scale(white_pawn, (square_size, square_size))

    white_rook = load_img("Chess_tile_rl.png")
    images['white_rook'] = pyg.transform.scale(white_rook, (square_size, square_size))

    white_knight = load_img("Chess_tile_nl.png")
    images['white_knight'] = pyg.transform.scale(white_knight, (square_size, square_size))

    white_bishop = load_img("Chess_tile_bl.png")
    images['white_bishop'] = pyg.transform.scale(white_bishop, (square_size, square_size))

    white_king = load_img("Chess_tile_kl.png")
    images['white_king'] = pyg.transform.scale(white_king, (square_size, square_size))

    white_queen = load_img("Chess_tile_ql.png")
    images['white_queen'] = pyg.transform.scale(white_queen, (square_size, square_size))
