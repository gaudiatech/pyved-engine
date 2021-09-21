"""
GUI sub-module,
 belongs to the katasdk_pym
"""
from katagames_sdk.capsule.event import EventReceiver
import katagames_sdk.capsule.pygame_provider as pprov


PygameBridge = pprov.get_module()


# pr GUI
class Etiquette:
    ft_obj = None

    def __init__(self, text, pos, rgb_color):
        if self.ft_obj is None:
            raise ValueError('use set_font(...) first! ')

        self._text = text
        self.pos = pos
        self._color = rgb_color
        self.img = self.ft_obj.render(self._text, True, self._color)

    @classmethod
    def set_font(cls, ft_obj):
        cls.ft_obj = ft_obj

    def get_text(self):
        return self._text

    def set_text(self, t):
        self._text = t
        self.img = self.ft_obj.render(self._text, True, self._color)


def test_func():
    print("Button clicked!")


class Button(EventReceiver):
    HIDEOUS_PURPLE = (255, 0, 255)

    def __init__(self, font, text, position_on_screen, callback=None, draw_background=True):
        super().__init__()
        padding_value = 12  # pixels

        if draw_background:
            self.bg_color = (100, 100, 100)
            self.fg_color = (255, 255, 255)
        else:
            self.bg_color = self.HIDEOUS_PURPLE
            self.fg_color = (0, 0, 0)

        # data
        self._callback = callback
        self._text = text
        self._hit = False

        # dawing
        self.font = font
        self.txt = text

        size = font.size(text)
        self.tmp_size = size
        self.position = position_on_screen
        self.collision_rect = PygameBridge.Rect(self.position, size).inflate(padding_value, padding_value)
        self.collision_rect.topleft = self.position

        self.image = None
        self.refresh_img()

    def refresh_img(self):
        self.image = PygameBridge.Surface(self.collision_rect.size).convert()
        self.image.fill(self.bg_color)

        if self.bg_color != self.HIDEOUS_PURPLE:
            textimg = self.font.render(self.txt, True, self.fg_color, self.bg_color)
        else:
            textimg = self.font.render(self.txt, False, self.fg_color)

        ssdest = self.image.get_size()
        ssource = textimg.get_size()
        blit_dest = (
            (ssdest[0] - ssource[0])//2,
            (ssdest[1] - ssource[1])//2
        )
        self.image.blit(textimg, blit_dest)

        #  TODO is this useful?
        # if self.bg_color == self.HIDEOUS_PURPLE:
        #     self.image.set_colorkey((self.bg_color))
        #     box_color = (190,) * 3
        #     full_rect = (0, 0, self.image.get_size()[0], self.image.get_size()[1])
        #     pygame.draw.rect(self.image, box_color, full_rect, 1)

    # pour des raisons pratiques (raccourci)
    def get_size(self):
        return self.image.get_size()

    def proc_event(self, ev, source):
        if ev.type == PygameBridge.KEYDOWN:
            self.on_keydown(ev)
        elif ev.type == PygameBridge.MOUSEMOTION:
            self.on_mousemotion(ev)
        elif ev.type == PygameBridge.MOUSEBUTTONDOWN:
            self.on_mousedown(ev)
        elif ev.type == PygameBridge.MOUSEBUTTONUP:
            self.on_mouseup(ev)

    def on_keydown(self, event):
        """
        Decides what do to with a keypress.
        special meanings have these keys: 
        enter, left, right, home, end, backspace, delete
        """
        if event.type != PygameBridge.KEYDOWN:
            print("textentry got wrong event: " + str(event))
        else:
            self.render()

    ### debug
    # if __name__=='__main__' and event.key == pygame.K_ESCAPE:
    #     events.RootEventSource.instance().stop()

    def on_mousedown(self, event):
        pos = event.pos
        if self.collision_rect.collidepoint(pos):
            if self._callback:
                self._callback()

    def on_mouseup(self, event):
        pos = event.pos
        # print('button: mouse button up detected! x,y = {}'.format(pos))

    def on_mousemotion(self, event):
        pass

    def set_callback(self, callback):
        self._callback = callback

    def render(self):
        """
        
        """
        pass

    def update(self):
        pass
    #     """
    #     Actually not needed. (only need if this module is run as a script)
    #     """
    #     # only need if this module is run as a script
    #     if __name__ == '__main__':
    #         screen = pygame.display.get_surface()
    #         screen.fill((100, 0, 0))
    #         screen.blit(self.image, self.position)
    #         pygame.display.flip()


class TextInput(EventReceiver):
    """
    Simple text entry component.
    """

    _caret_color = (90, 90, 90)
    _padding = 4  # en px

    def __init__(self, nickname, font, how_to_process_cb, pos, width=300):
        """
        nickname: nickname, all messages will be prefixed with the nickname
        font    : pygame.font.Font object
        width   : in pixel that this element can use (this restricts the number
                  of char you can enter

        events:
        in : pygame.KEYDOWN
        out: eventtypes.CHATMSG
        """
        super().__init__()

        self.position = pos
        # test que le 3e arg est callable...
        assert hasattr(how_to_process_cb, '__call__')
        self.on_enter_func = how_to_process_cb

        self.pwd_field = False

        # data
        self.__txt_content = ""
        self.caretpos = 0
        self.max = 255
        self.nickname = nickname

        # drawing
        self.dirty = True
        self.font = font
        height = self.font.get_ascent() - self.font.get_descent() + 8
        self.image = PygameBridge.Surface((width, height)).convert()
        self.size = (width, height)

        self.text_color = (1, 1, 1)
        self.text_field_rect = PygameBridge.Rect(0, 0, width - 1, height - 1)
        self.text_img = PygameBridge.Surface((2, 2))
        self.pixel_width = width - 4

        self._focus = None
        self.fill_color = None
        self.no_focus()

    def has_focus(self):
        return self._focus

    def get_disp_text(self):
        if self.pwd_field:
            return TextInput.hide_text(self.__txt_content)
        return self.__txt_content

    def focus(self):
        self._focus = True
        self.fill_color = (220, 220, 220)
        self.render_field()

    def no_focus(self):
        self._focus = False
        self.fill_color = (100, 100, 100)
        self.render_field()

    def contains(self, scr_pos):
        w, h = self.image.get_size()
        a, b = self.position[0], self.position[0] + w
        c, d = self.position[1], self.position[1] + h
        x, y = scr_pos
        if (a < x < b) and (c < y < d):
            return True
        return False

    @staticmethod
    def hide_text(txt_content):
        tmp = ['*' for i in range(len(txt_content))]
        return ''.join(tmp)

    def proc_event(self, event, source):
        if event.type != PygameBridge.KEYDOWN:
            return

        # - traitement touche pressée
        if event.key == PygameBridge.K_RETURN:
            # self.on_enter()
            self.on_enter_func(self.__txt_content)
            self.__txt_content = ''
            self.caretpos = 0

        elif event.key == PygameBridge.K_RIGHT:
            self.move_caret(+1)

        elif event.key == PygameBridge.K_LEFT:
            self.move_caret(-1)

        elif event.key == PygameBridge.K_HOME:
            self.move_caret('home')

        elif event.key == PygameBridge.K_END:
            self.move_caret('end')

        elif event.key == PygameBridge.K_BACKSPACE:
            self.backspace_char()

        elif event.key == PygameBridge.K_DELETE:
            self.delete_char()

        elif event.key == PygameBridge.K_TAB:
            pass

        else:
            if event.unicode != '':
                if len(self.__txt_content) < self.max:
                    self.__txt_content = self.__txt_content[:self.caretpos] + event.unicode + self.__txt_content[
                                                                                              self.caretpos:]
                    self.caretpos += 1
        self.render_field()

    def move_caret(self, steps):
        """
        Moves the caret about steps. Positive numbers moves it right, negative
        numbers left.
        """
        if steps == 'home':
            self.caretpos = 0
        elif steps == 'end':
            self.caretpos = len(self.__txt_content)
        else:
            assert isinstance(steps, int)
            self.caretpos += steps

        if self.caretpos < 0:
            self.caretpos = 0
        if self.caretpos > len(self.__txt_content):
            self.caretpos = len(self.__txt_content)

    def backspace_char(self):
        """
        Deltes the char befor the caret position.
        """
        if self.caretpos > 0:
            self.__txt_content = self.__txt_content[:self.caretpos - 1] + self.__txt_content[self.caretpos:]
            self.caretpos -= 1

    def delete_char(self):
        """
        Deltes the char after the caret position.
        """
        self.__txt_content = self.__txt_content[:self.caretpos] + self.__txt_content[self.caretpos + 1:]

    def render_field(self):
        """
        Renders the string to self.image.
        """
        self.image.fill(self.fill_color)
        content = self.get_disp_text()

        if len(content):
            # while self.font.size(content)[0] > self.pixel_width:
            #    self.backspace_char()
            self.text_img = self.font.render(content, 1, self.text_color, self.fill_color)
            self.image.blit(self.text_img, (2, 2))

            # - draw caret
            # TODO fix pygame draw line
            # xpos = self.font.size(content[:self.caretpos])[0] + 2
            # pygame.draw.line(self.image, self._caret_color, (xpos, self._padding),
            #                  (xpos, self.image.get_height() - self._padding), 2)

        PygameBridge.draw.rect(self.image, (100, 100, 100), self.text_field_rect, 2)
