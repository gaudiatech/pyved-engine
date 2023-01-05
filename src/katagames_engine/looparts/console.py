import re
import textwrap

from .. import _hub as inj
from ..compo import vscreen as core


pygame = inj.pygame

# - options
# --------------- constants for IgCustomConsole display formattage -------------
CONSOLE_FT_SIZE = 12
omega_ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
ANTIALIAS_OPT = False


# - addons - - > DU TAF PROSPECTIF
# EventReicever = kengi.event.EventReceiver
#
# class IgConsoleCtrl(EventReicever):
#     def proc_event(self, ev, source):
#         pass
#
# class IgConsoleView(EventReicever):
#     def proc_event(self, ev, source):
#         pass


# --------------- SYNTAX DETECTORS FOR IgCustomConsole --------------
re_token = re.compile(r"""[\"].*?[\"]|[\{].*?[\}]|[\(].*?[\)]|[\[].*?[\]]|\S+""")
re_is_list = re.compile(r'^[{\[(]')

# re_is_number = re.compile(r"""
# (?x)
# [-]?[0][x][0-9a-fA-F]+[lLjJ]? | 	#  Hexadecimal
# [-]?[0][0-7]+[lLjJ]? |				#  Octal
# [-]?[\d]+(?:[.][\d]*)?[lLjJ]?		#  Decimal (Int or float)
#""")
re_is_number = re.compile("(?x)[-]?[\d]+(?:[.][\d]*)?[lLjJ]?")  # decimal only

re_is_assign = re.compile(r'[$](?P<name>[a-zA-Z_]+\S*)\s*[=]\s*(?P<value>.+)')
re_is_comment = re.compile(r'\s*#.*')
re_is_var = re.compile(r'^[$][a-zA-Z_]+\w*\Z')


# -------------------- outils pr implementation CustomIgConsole -------------------
class ParseError(Exception):
    def __init__(self, token):
        self.token = token

    def at_token(self):
        return self.token


def balanced(t):  # UTIL func used in .tokenize
    stack = []
    pairs = {"\'": "\'", '\"': '\"', "{": "}", "[": "]", "(": ")"}
    for char in t:
        if stack and char == pairs[stack[-1]]:
            stack.pop()
        elif char in pairs:
            stack.append(char)
    return not bool(stack)


# ----------------------- classe essentielle au plugin -----------------------------
class CustomConsole:
    """
    en phase de devenir le MODELE, a separer de la vue...
    """

    def __init__(self, screen, rect, functions=None, key_calls=None, vari=None, syntax=None, fontobj=None):
        """
        :param screen:
        :param rect:
        :param functions:
        :param key_calls:
        :param vari:
        :param syntax: dict that associates v,k where
           v is a regexp processor
           k is a function in the form console_func(console, match) that calls console.output(...)
        """
        self.message_of_the_day = ["no Motd"]
        self.scrref = screen
        self.li_raw_lines_labels = list()

        self.bg_color = '#06170e'  # very dark green

        self.bg_alpha = 200  # how transparent is the Console Background, 255 -> opaque
        self.txt_color_i = (0, 255, 0)  # Green bright Input Color
        self.txt_color_o = (0, 153, 0)  # Dark Green output Color

        self.changed = True
        self.active = False
        self.preserve_events = True
        self.repeat_rate = [500, 30]

        self.ps1 = "x "
        self.ps2 = ">>> "  # invite cmd
        self.ps3 = "... "
        self.pos_sym_char = "_"
        self.line_disp_yoffset = -2  # how many pixels shll i move it?

        self.c_ps = self.ps2

        # --- c_out is the history of all text
        # -- c_hist is the history of all commands
        self.c_out = ['',]
        self.c_in = ""
        self.c_hist = [""]
        self.c_hist_pos = 0
        self.c_pos = 0
        self.c_draw_pos = 0
        self.c_scroll = 0

        #self.parent_screen = screen

        self.rect = pygame.Rect(rect)
        self.base_x, self.base_y = self.rect[0], self.rect[1]

        self.size = self.rect.size

        self._fontsize = 18
        if fontobj is None:
            self.font = pygame.font.Font(None, self._fontsize)
        else:
            self.font = fontobj
        # en remplacement de:
        # adhoc_ft_size = CONSOLE_FT_SIZE if (ftsize is None) else ftsize
        # print('CONSOLE uses font {}, size{}'.format(fontpath, adhoc_ft_size))
        # self.font = pygame.font.Font(fontpath, adhoc_ft_size)
        self.font_height = self.font.get_linesize()

        self.max_lines = int((self.size[1] / self.font_height) - 1)
        ftdim = self.font.size(omega_ascii_letters)
        kappa = ftdim[0] / len(omega_ascii_letters)

        self.max_chars = int(((self.size[0]) / kappa) - 1)
        self.txt_wrapper = textwrap.TextWrapper()
        self.bg_layer = pygame.Surface(self.size)

        # TODO use alpha!
        # self.bg_layer.set_alpha(self.bg_alpha)

        self.txt_layer = pygame.Surface(self.size)
        self.txt_layer.set_colorkey(self.bg_color)

        pygame.key.set_repeat(*self.repeat_rate)

        self.key_calls = {}
        self.func_calls = {}
        self.user_vars = vari
        self.user_syntax = syntax
        self.user_namespace = {}

        self.add_key_calls({"l": self.clear, "c": self.clear_input, "w": self.toggle_active})
        self.add_key_calls(key_calls)

        self.add_functions_calls({"help": self.help, "echo": self.output, "clear": self.clear})
        self.add_functions_calls(functions)

        self.cb_func = None

    @property
    def font_size(self):
        return self._fontsize

    @font_size.setter
    def font_size(self, new_val):
        self._fontsize = new_val
        self.font = pygame.font.Font(None, new_val)
        # need to update this, as well
        self.font_height = self.font.get_linesize()
        self.changed = True

    def set_motd(self, msg):
        self.message_of_the_day = msg.splitlines()
        self.c_out.extend(self.message_of_the_day)

    def add_functions_calls(self, functions):
        if isinstance(functions, dict):
            self.func_calls.update(functions)

    def add_key_calls(self, functions):
        if isinstance(functions, dict):
            self.key_calls.update(functions)

    def output(self, text):
        """Print a string on the Console. Use: echo "Test Test Test" """
        self.changed = True
        if not isinstance(text, str):
            text = str(text)
        text = text.expandtabs()
        text = text.splitlines()
        self.txt_wrapper.width = self.max_chars
        for line in text:
            for w in self.txt_wrapper.wrap(line):
                self.c_out.append(w)

    def submit_input(self, text):
        self.clear_input()
        if self.cb_func:
            self.output(text)
        else:
            self.output(self.c_ps + text)

        self.c_scroll = 0
        if self.cb_func:
            self.cb_func(text)
            self.cb_func = None
        else:
            self.send_pyconsole(text)

    def format_input_line(self):
        text = self.c_in[:self.c_pos] + self.pos_sym_char + self.c_in[self.c_pos + 1:]
        n_max = int(self.max_chars - len(self.c_ps))
        vis_range = self.c_draw_pos, self.c_draw_pos + n_max
        if self.cb_func:
            prefix = ''
        else:
            prefix = self.c_ps
        return prefix + text[vis_range[0]:vis_range[1]]

    def str_insert(self, text, strn):
        string = text[:self.c_pos] + strn + text[self.c_pos:]
        self.set_pos(self.c_pos + len(strn))
        return string

    def clear_input(self):
        self.c_in = ""
        self.c_pos = 0
        self.c_draw_pos = 0

    def set_pos(self, newpos):
        self.c_pos = newpos
        if (self.c_pos - self.c_draw_pos) >= int(self.max_chars - len(self.c_ps)):
            self.c_draw_pos = max(0, int(self.c_pos - (self.max_chars - len(self.c_ps))))
        elif self.c_draw_pos > self.c_pos:
            self.c_draw_pos = self.c_pos - (self.max_chars/2)
            if self.c_draw_pos < 0:
                self.c_draw_pos = 0
                self.c_pos = 0

    def toggle_active(self):
        self.active = not self.active

    def activate(self):
        self.active = True

    def desactivate(self):
        self.active = False

    def add_to_history(self, text):
        self.c_hist.insert(-1, text)
        self.c_hist_pos = len(self.c_hist) - 1

    def draw(self):
        if not self.active:
            return

        if self.changed:  # update text layer
            del self.li_raw_lines_labels[:]
            # creation du txt layer
            self.txt_layer.fill(self.bg_color)
            lines = self.c_out[-(self.max_lines + self.c_scroll):len(self.c_out) - self.c_scroll]
            y_pos = self.size[1]-(self.font_height*(len(lines)+1))
            for line in lines:
                if line == '':
                    self.li_raw_lines_labels.append(None)
                else:
                    label_surf = self.font.render(line, False, self.txt_color_o, (0, 0, 0))
                    dpos = (self.base_x, self.base_y+y_pos+self.line_disp_yoffset)
                    # self.txt_layer.blit(label_surf, dpos )
                    self.li_raw_lines_labels.append([label_surf, dpos])
                y_pos += self.font_height

            if self.format_input_line() == '':
                self.li_raw_lines_labels.append(None)
            else:
                last_label = self.font.render(self.format_input_line(), False, self.txt_color_i)
                last_pos = (self.base_x, self.base_y + self.size[1] - self.font_height + self.line_disp_yoffset)
                # self.txt_layer.blit(last_label, last_pos)
                self.li_raw_lines_labels.append([last_label, last_pos])

            # refresh bg_layer qui contiendra aussi txt_layer...
            # self.bg_layer = pygame.Surface(self.size)
            # self.bg_layer.blit(self.txt_layer, (0, 0)) #, 0, 0))
            self.changed = False

        self.bg_layer.fill(self.bg_color)
        self.scrref.blit(self.bg_layer, (self.base_x, self.base_y))

        for liraw_elt in self.li_raw_lines_labels:
            if liraw_elt:
                label, lpos = liraw_elt
                self.scrref.blit(label, lpos)

    def keyhandler(self, event):
        if self.active:
            self.changed = True
            # Special Character Manipulation
            if event.key == pygame.K_TAB:
                self.c_in = self.str_insert(self.c_in, "    ")
            elif event.key == pygame.K_BACKSPACE:
                if self.c_pos > 0:
                    self.c_in = self.c_in[:self.c_pos - 1] + self.c_in[self.c_pos:]
                    self.set_pos(self.c_pos - 1)
            elif event.key == pygame.K_DELETE:
                if self.c_pos < len(self.c_in):
                    self.c_in = self.c_in[:self.c_pos] + self.c_in[self.c_pos + 1:]
            elif event.key == pygame.K_RETURN or event.key == 271:
                self.submit_input(self.c_in)
            # Changing Cursor Position
            elif event.key == pygame.K_LEFT:
                if self.c_pos > 0:
                    self.set_pos(self.c_pos - 1)
            elif event.key == pygame.K_RIGHT:
                if self.c_pos < len(self.c_in):
                    self.set_pos(self.c_pos + 1)
            elif event.key == pygame.K_HOME:
                self.set_pos(0)
            elif event.key == pygame.K_END:
                self.set_pos(len(self.c_in))
            # History Navigation
            elif event.key == pygame.K_UP:
                if len(self.c_out):
                    if self.c_hist_pos > 0:
                        self.c_hist_pos -= 1
                    self.c_in = self.c_hist[self.c_hist_pos]
                    self.set_pos(len(self.c_in))
            elif event.key == pygame.K_DOWN:
                if len(self.c_out):
                    if self.c_hist_pos < len(self.c_hist) - 1:
                        self.c_hist_pos += 1
                    self.c_in = self.c_hist[self.c_hist_pos]
                    self.set_pos(len(self.c_in))
            # Scrolling
            elif event.key == pygame.K_PAGEUP:
                if self.c_scroll < len(self.c_out) - 1:
                    self.c_scroll += 1
            elif event.key == pygame.K_PAGEDOWN:
                if self.c_scroll > 0:
                    self.c_scroll -= 1
            # Normal character printing
            elif event.key >= 32:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    if event.key in range(256) and chr(event.key) in self.key_calls:
                        self.key_calls[chr(event.key)]()
                else:
                    char = str(event.unicode)
                    self.c_in = self.str_insert(self.c_in, char)

    def send_pyconsole(self, text):
        if not text:  # Output a blank row if nothing is entered
            self.output("")
            return

        self.add_to_history(text)

        # Determine if the statement is an assignment
        assign = re_is_assign.match(text)

        # If it is tokenize only the "value" part of $name = value
        if assign:
            tokens = self.tokenize(assign.group('value'))
        else:
            tokens = self.tokenize(text)

        if tokens is None:
            return

        # Evaluate
        try:
            out = None
            # A variable alone on a line
            if (len(tokens) == 1) and re_is_var.match(text) and not assign:
                out = tokens[0]
            # Statement in the form $name = value
            elif (len(tokens) == 1) and assign:
                self.setvar(assign.group('name'), tokens[0])
            else:
                # Function
                if tokens[0] not in self.func_calls:
                    self.output("Unknown Command: " + str(tokens[0]))
                    self.output(r'Type "help" for a list of commands.')
                else:
                    out = self.func_calls[tokens[0]](*tokens[1:])
                    if out is None:
                        print('*Warning console func MUST return a value*')
                    # Assignment from function's return value
                    if assign:
                        self.setvar(assign.group('name'), out)
                    if out is not None:
                        self.output(out)

        except ValueError as ve:
            self.output("Error: {0}".format(ve))
        except TypeError as te:
            tmp = "Error {0}".format(te)
            if tmp.find('missing') < 0:
                self.output(tmp)
            else:
                self.output("Bad syntax, type help cmd for more info")

    def setvar(self, name, value):
        """Sets the value of a variable"""
        if name in self.user_vars or name not in self.__dict__:
            self.user_vars.update({name: value})
            self.user_namespace.update(self.user_vars)
        elif name in self.__dict__:
            self.__dict__.update({name: value})

    def convert_token(self, tok):
        """
        TODO tomanalyz
        -this is one of the most important func
        :param tok:
        :return:
        """
        tok = tok.strip("$")
        try:
            tmp = eval(tok, self.__dict__, self.user_namespace)
            return tmp

        except SyntaxError as strerror:
            self.output("SyntaxError: " + str(strerror))
            raise ParseError(tok)

        except TypeError as strerror:
            self.output("TypeError: " + str(strerror))
            raise ParseError(tok)

        except NameError as strerror:
            self.output("NameError: " + str(strerror))

        self.output("Error:")
        raise ParseError(tok)

    def tokenize(self, s):
        if re_is_comment.match(s):
            return [s]

        for r in self.user_syntax:
            group = r.match(s)
            if group:
                self.user_syntax[r](self, group)
                return

        tokens = re_token.findall(s)
        tokens = [i.strip("\"") for i in tokens]
        cmd = []
        i = 0
        while i < len(tokens):
            t_count = 0
            val = tokens[i]

            if re_is_number.match(val):
                cmd.append(self.convert_token(val))
            elif re_is_var.match(val):
                cmd.append(self.convert_token(val))
            elif val == "True":
                cmd.append(True)
            elif val == "False":
                cmd.append(False)
            elif re_is_list.match(val):
                while not balanced(val) and (i + t_count) < len(tokens) - 1:
                    t_count += 1
                    val += tokens[i + t_count]
                else:
                    if (i + t_count) < len(tokens):
                        cmd.append(self.convert_token(val))
                    else:
                        raise ParseError(val)
            else:
                cmd.append(val)
            i += t_count + 1
        return cmd

    def clear(self):
        """Clear the screen! Use: clear"""
        del self.li_raw_lines_labels[:]
        self.c_out = [" "]
        self.c_scroll = 0
        return "[Screen Cleared]"

    def help(self, *args):
        if args:
            items = list()
            for cfunc_name in self.func_calls:
                if cfunc_name in args:
                    e = (cfunc_name, self.func_calls[cfunc_name])
                    items.append(e)

            for name, v in items:
                nb_args = v.__code__.co_argcount
                if nb_args > 0:
                    nb_args -= 1 if v.__code__.co_varnames[0] == "self" else 0
                out = "{} :: Takes {} arguments,".format(name, nb_args)
                doc = v.__doc__
                if doc:
                    out += textwrap.dedent(doc)
                tmp_indent = self.txt_wrapper.subsequent_indent
                self.txt_wrapper.subsequent_indent = " " * (len(name) + 2)
                self.output(out)
                self.txt_wrapper.subsequent_indent = tmp_indent
        else:
            out = "Available commands are\n"
            lc = list(self.func_calls.keys())
            lc.sort()
            out += '; '.join(lc)
            self.output(out)
            self.output(r'Type "help command-name" for more information on that command')
