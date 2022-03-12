VYEAR_2DIG = 22  # remember to use only 2 digits
VMONTH = 3
_idx = 1  # 1 for alpha, 2 for beta etc.
VRTYPE = ['','a','b','rc'][_idx]  # do not change this line
VRANK = 2

"""
To respect the PEP440, do not modify the code below

We target this standard:
- Alpha release     yy.MMaN
- Beta release      yy.MMbN
- Release candidate yy.MMrcN
- Final release     yy.MM
"""

_suffix = '' if '' == VRTYPE else VRTYPE+str(VRANK)
ENGI_VERSION = f"{VYEAR_2DIG}.{VMONTH}{_suffix}"
