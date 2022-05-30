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

HD_DISP = 'hd'
OLD_SCHOOL_DISP = 'old_school'
SUPER_RETRO_DISP = 'super_retro'
CUSTOM_DISP = 'custom'
OMEGA_DISP_CODES = (
    HD_DISP, OLD_SCHOOL_DISP, SUPER_RETRO_DISP, CUSTOM_DISP
)

USEREVENT = 27

FIRST_ENGIN_TYPE = USEREVENT + 1
FIRST_CUSTO_TYPE = FIRST_ENGIN_TYPE + 20  # therefore, 20 is the maximal amount of engine events
