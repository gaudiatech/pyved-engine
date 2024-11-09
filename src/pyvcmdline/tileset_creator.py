import copy
import json
from PIL import Image

def create_json_for_tileset(file_name, img_dim, tile_size):
    width, height = img_dim
    tile_width, tile_height = tile_size

    cols = width // tile_width
    rows = height // tile_height

    frame = {
        "frame": {
            "x": "_X_",
            "y": "_Y_",
            "w": tile_width,
            "h": tile_height
        },
        "rotated": False,
        "trimmed": False,
        "spriteSourceSize": {
            "x": 0,
            "y": 0,
            "w": tile_width,
            "h": tile_height
        },
        "sourceSize": {
            "w": tile_width,
            "h": tile_height
        }
    }

    data = {
        "frames": {},
        "meta": {
            "app": "http://www.codeandweb.com/texturepacker",
            "version": "1.0",
            "image": f"{file_name}.png",
            "format": "RGBA8888",
            "size": {
                "w": width,
                "h": height
            },
            "scale": "1"
        }
    }

    index = 0
    for r in range(rows):
        for c in range(cols):
            f = copy.deepcopy(frame)
            f["frame"]["x"] = c * tile_width
            f["frame"]["y"] = r * tile_height
            data["frames"][f"{index}.png"] = f
            index += 1

    with open(f"{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def suggest_tile_sizes(minsize, image_path, spacing):
    img = Image.open(image_path)
    width, height = img.size
    print(f"Image dimensions: {width}x{height}")
    print(f"Spacing between tiles: {spacing}\n")

    possible_tile_sizes = []

    max_tile_width = width
    max_tile_height = height

    for tile_width in range(minsize, max_tile_width + 1):
        for tile_height in range(minsize, max_tile_height + 1):
            denominator_width = tile_width + spacing
            denominator_height = tile_height + spacing
            if denominator_width == 0 or denominator_height == 0:
                continue

            tiles_across = (width + spacing) / denominator_width
            tiles_down = (height + spacing) / denominator_height

            if tiles_across.is_integer() and tiles_down.is_integer():
                possible_tile_sizes.append({
                    'tile_width': tile_width,
                    'tile_height': tile_height,
                    'tiles_across': int(tiles_across),
                    'tiles_down': int(tiles_down)
                })
    
    candidates = []
    if possible_tile_sizes:
        print("Compute suggestions...")
        for suggestion in possible_tile_sizes:
            print(f"- Tile Size: {suggestion['tile_width']}x{suggestion['tile_height']} px, "
                  f"Tiles Across: {suggestion['tiles_across']}, "
                  f"Tiles Down: {suggestion['tiles_down']}")
            candidates.append((suggestion['tile_width'], suggestion['tile_height']))
    else:
        print("No suitable tile sizes found with the given spacing.")
    return (width, height), candidates


def start_creation(image_path):
    minsize_given = int(input("Enter the minimal value (in pixels) you believe a tile can have: "))
    spacing = int(input("Enter spacing value please (in pixels): "))
    
    img_size, tsize_candidates = suggest_tile_sizes(minsize_given, image_path, spacing)
    print()
    print('-'*32)
    print('Possible values for tile sizes are:')
    for k, val in enumerate(tsize_candidates):
        print(f'{k} --> {val}')
    chosen_k = int(input('Look at the image, then select the right tile_size candidate.Index? '))
    tsize = tsize_candidates[chosen_k]
    create_json_for_tileset(image_path.split('.')[0], img_size, tsize)
    print('JSON file created successfully!')
