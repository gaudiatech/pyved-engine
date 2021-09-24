# Frequently asked questions


## TERMS OF USE/ LICENSING

#### -Q. is the SDK free to use? 

Yes. Have fun tinkering with it!

#### -Q. I plan to distribute games made with KataSDK, is it OK?

Yes for showcasing your skills/sharing game jam-related creations.

For *commercial games*, you would need to contact directly the author of KataSDK author: thomas at gaudia-tech.com.
describe your game (where/how you plan to sell it) and simply request a written permission.


#### -Q. How open-source is this tool?

While the ENGINE and API are fully 100% open-source and free-to-use (license LGPL3), there are a few parts of the SDK that remain private.

The tool has been created **first and foremost** to foster the growth of the new [Kata.games platform](https://kata.games).
So all planned upgrades go in that direction.

The amount of work required to create such a tool seems to go beyond what a reasonable human being would accomplish for free.
(1200+ hours of work to find a working architecture, implementing features and software components one by one using 3 different programming languages).


## DEVELOPER COMMUNITY

#### -Q. Why is there a limited choice in screen resolution/ upscaling?
Multiple reasons have led to this design principle:

1.  Due to html5 standards (properties & upscaling) and how browser handle things, a fixed resolution/ scaling factor is very useful. Right now there is a vicious bug (strong antialias effect) when the upscaling is active and this is destroying how good your pixel art can look… But this bug can and will be fixed! More or less I already know the fix. However it would be almost impossible to apply a patch if there was no constraint on resolution & scaling, as far a I know. This is the main reason, and by far the most important one.
2. **_Integration within a web app_** is made very simple, and not error-prone at all thanks to the static html5 canvas size. The more complex your web app is, the more useful this characteristic becomes.
3. I like the idea that game creators are challenged to play around the immutable idea of what "the game screen" is, just like in the [PICO8 vm](https://www.lexaloffle.com/pico-8.php) community for example,
 where one has to be creative within a smaller space of possibilities. In the long run this could improve the quality of content hosted on [Kata.games](https://kata.games)
 

#### -Q. I need to ask precise dev-related questions/ report bugs. Do you have a Discord?

Yes! Please join the discussion/participate [here!](https://discord.gg/3NFfvHAt44)

 
#### -Q. Where can I see patch notes/the version history?

Your can check [this file](https://games.gaudia-tech.com/sdk-patch-notes.txt)
Or please refer to the [version history (PyPi project page)](https://pypi.org/project/katasdk/#history).
 
#### -Q. are there "real games" coded using this tool?

It's not ready yet as this tool is not mature enough (but it is improving).

Cool playable demos are already available and can be tested here: [kata.games](https://kata.games)


## MISCELLANEOUS

#### -Q. who created this tool?

Thomas "wkta" Iwaszko,

with a great contribution from Pierre Quentel who has designed the Brython (project foundations).

If you wish to contact me directly you can find my e-mail somewhere in code comments,
on [my github profile](https://github.com/wkta), or DM me via Discord: `IW.Tom#7412`



