# Load one image file, use it for multiple images.

import pygame
import weakref
from . import render_text, TEXT_COLOR
import katagames_engine as kengi


# Keep a list of already-loaded images, to save memory when multiple objects
# need to use the same image file.
pre_loaded_images = weakref.WeakValueDictionary()

DEFAULT_COLOR_KEY = (255, 0, 255)


class Image(object):
    def __init__(self, fname=None, frame_width=0, frame_height=0, custom_frames=None,
                 flags=0, color_key=DEFAULT_COLOR_KEY, transparent=False):
        """Load image file, or create blank image, at frame size"""
        if fname:
            self.bitmap = self.get_pre_loaded(fname, transparent)
            if not self.bitmap:
                self.bitmap = pygame.image.load(fname).convert_alpha()
                self.bitmap.set_colorkey(color_key, flags)
        else:
            self.bitmap = pygame.Surface((frame_width, frame_height))
            self.bitmap.fill(color_key)
            self.bitmap.set_colorkey(color_key, flags)

        self.fname = fname
        self.flags = flags
        self.transparent = transparent
        self.color_key = color_key
        if transparent:
            alpha = int(transparent)
            if alpha <= 1:
                alpha = 155
            self.bitmap.set_alpha(alpha)

        if frame_width == 0:
            frame_width = self.bitmap.get_width()
        if frame_height == 0:
            frame_height = self.bitmap.get_height()

        if frame_width > self.bitmap.get_width():
            frame_width = self.bitmap.get_width()
        self.fname = fname
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.custom_frames = custom_frames

    @staticmethod
    def get_pre_loaded(ident, transparent):
        return pre_loaded_images.get((ident, transparent))

    @staticmethod
    def record_pre_loaded(ident, colorset, bitmap, transparent=False):
        pre_loaded_images[(ident, repr(colorset), transparent)] = bitmap

    def _get_frame_area(self, frame):
        if self.custom_frames and frame < len(self.custom_frames):
            area = pygame.Rect(self.custom_frames[frame])
        else:
            frames_per_row = self.bitmap.get_width() // self.frame_width
            area_x = (frame % frames_per_row) * self.frame_width
            area_y = (frame // frames_per_row) * self.frame_height
            area = pygame.Rect(area_x, area_y, self.frame_width, self.frame_height)
        return area

    def render(self, dest=(0, 0), frame=0, dest_surface=None ):
        # Render this Image onto the provided surface.
        # Start by determining the correct sub-area of the image.
        area = self._get_frame_area(frame)
        dest_surface = dest_surface or kengi.core.get_screen()  # new way to retrieve the surface used for display

        dest_surface.blit(self.bitmap, dest, area)

    def render_c(self, dest=(0, 0), frame=0, dest_surface=None ):
        # As above, but the dest coordinates point to the center of the image.
        area = self._get_frame_area(frame)

        dest_c = self.get_rect(frame)
        dest_c.center = dest
        dest_surface = dest_surface or kengi.core.get_screen()  # new way to retrieve the surface used for display

        dest_surface.blit(self.bitmap, dest_c, area)

    def get_subsurface(self, frame):
        # Return one of the frames as a pygame subsurface.
        area = self._get_frame_area(frame)
        return self.bitmap.subsurface(area)

    def get_rect(self, frame):
        # Return a rect of the correct size for this frame.
        if self.custom_frames and frame < len(self.custom_frames):
            return pygame.Rect(0, 0, self.custom_frames[frame][2], self.custom_frames[frame][3])
        else:
            return pygame.Rect(0, 0, self.frame_width, self.frame_height)

    def num_frames(self):
        if self.custom_frames:
            return len(self.custom_frames)
        else:
            frames_per_row = self.bitmap.get_width() // self.frame_width
            frames_per_column = self.bitmap.get_height() // self.frame_height
            return frames_per_row * frames_per_column

    def __reduce__(self):
        # Rather than trying to save the bitmap image, just save the parameters.
        return Image, (self.fname, self.frame_width, self.frame_height, self.custom_frames, self.flags,
                       self.color_key, self.transparent)

    def tile(self, dest=None, frame=0, dest_surface=None, x_offset=0, y_offset=0):
        dest_surface = dest_surface or kengi.core.get_screen()  # new way to retrieve the surface used for display

        if not dest:
            dest = dest_surface.get_rect()
        grid_w = dest.w // self.frame_width + 2
        grid_h = dest.h // self.frame_height + 2
        dest_surface.set_clip(dest)
        my_rect = pygame.Rect(0, 0, 0, 0)

        for x in range(-1, grid_w):
            my_rect.x = dest.x + x * self.frame_width +x_offset
            for y in range(-1, grid_h):
                my_rect.y = dest.y + y * self.frame_height +y_offset
                self.render(my_rect, frame, dest_surface)

        dest_surface.set_clip(None)

    def copy(self,ident=None):
        nu_sprite = Image(frame_height=self.frame_height,frame_width=self.frame_width,)
        nu_sprite.bitmap = self.bitmap.copy()
        if ident:
            self.record_pre_loaded(ident, None, nu_sprite.bitmap)
        return nu_sprite


class TextImage(Image):
    def __init__(self, txt='?????', frame_width=128, color=None, font=None):
        """Create an image of the provided text"""
        if not color:
            color = TEXT_COLOR

        self.txt = txt
        self.bitmap = render_text(font, txt, frame_width, color, justify=0, antialias=False)
        self.frame_width = self.bitmap.get_width()
        self.frame_height = self.bitmap.get_height()
        self.custom_frames = None

    def __reduce__(self):
        # Rather than trying to save the bitmap image, just save the reconstruction details.
        return TextImage, (self.txt, self.frame_width, self.frame_height)


