import base64

#I used base64.b64encode(fptr)...
# Use base64.b64decode(encoded) to decode!

f = open('capello-ft.json', 'r')
#base64.b64encode(f.read())
s = f.read()


import re
s = re.sub('[\s+]', '', s)
with open('packedjson.py', 'w') as f2:
    print('content='+s,file=f2)

f.close()
print('done.')
