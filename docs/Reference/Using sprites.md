
Using sprites is an important part of any game creation task!

To make this process more easy, **PYV** provides a standard format that you can use
out-of-the-box and is compatible with web technologies.

A *spritesheet* is basically a huge image that stores all your sprites.
By using both a `.png` and a `.json` file that acts like a global index with a set
of coordinates, the game engine empowers you by quickly loading all your sprites, and these
sprites become available within your source-code context.

To describe this quickly, and make things less abstract here's
a minimalistic example of how you can handle your *spritheets*:

- [Json map](https://github.com/gaudiatech/pyved-engine/blob/master/src/cartes.json)
- [Image file](https://github.com/gaudiatech/pyved-engine/blob/master/src/cartes.png)

The source-code that uses these files can be viewed
 [Here, at the given line](https://github.com/gaudiatech/pyved-engine/blob/master/src/cards_testing.py#L55).
As you can see, the parameter provided is simply the name of the *spritesheet*, 
with no file extension. You can, however specify a path.

To create *spritesheets* that stick to this format you need some tools.

Here is the tool that allows you to pack or unpack *spritesheets*
[TexturePacker Online](https://www.codeandweb.com/tp-online)
