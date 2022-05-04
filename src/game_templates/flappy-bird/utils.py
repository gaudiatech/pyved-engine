import katagames_engine as kengi


def load_image(path, alpha=False, scale=1.0, color_key=None):
    img = kengi.pygame.image.load(path)
    if alpha:
        img = img.convert_alpha()
    else:
        img = img.convert()
    if scale != 1.0:
        tmp = img.get_size()
        destsize = (int(scale*tmp[0]), int(scale*tmp[1]))
        img = kengi.pygame.transform.scale(img, destsize)
    if color_key:
        img.set_colorkey(color_key)
    return img


def clamp(value, mini, maxi):
    if value < mini:
        return mini
    if value > maxi:
        return maxi
    return value
