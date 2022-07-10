"""
constants only
--------------
in regard to display options,
within KENGI there are only 4 canonical modes for display:

three that are displayed in a 960 x 720 -pixel canvas
'super_retro' (upscaling x3), 'old_school', (upscaling x2), 'hd' (no upscaling)

one that is displayed in a user-defined size canvas and also uses
a pixel-to-pixel mapping just like the 'hd' option
"""
STD_SCR_SIZE = (960, 720)

USEREVENT = 32850  # pygame userevent 2.1.1

FIRST_ENGIN_TYPE = USEREVENT + 1
FIRST_CUSTO_TYPE = FIRST_ENGIN_TYPE + 20  # therefore, 20 is the maximal amount of engine events
