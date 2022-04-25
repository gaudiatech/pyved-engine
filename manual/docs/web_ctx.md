# Run games in the Web Context

## Pre-requisites, game structure

You need to have the `katasdk` installed. Moreover for version `0.0.5` or inferior,
you would need to put all your code in `main.py`.

You need a folder named `assets/` and a JSON-file name `assets.json` that lists all images your game is using.

Example of such a file:

```
[
  'explo_sprsheet.png',
  'minerals.png',
  'my-plane.png',
  'myspace.png',
  'sc-trail.png',
  'sc-trail-maxpower.png',
  'space_mine.png'
]
```
Don't add any symbols except the braces. Spaces or newlines do not matter.

## webtest VS bundle

The two choices for a developer are: test your game / bundle your game for the web.

It is important to understand that a game in the "web bundle" or "wbundle" format is supposed to be distributed. 
This means **you only bundle a game once it is finished!**
For bundling you need a dev account, also the number of games you can bundle is limited to 3 for now.

### Testing your game in a web context: how-to

Open a command line interface (you can run `cmd.exe` if you're using Windows).
Go to the directory parent to your project (one step below the project's root folder), then type this command:

    katasdk webtest folder/

This will create a temporary web bundle.
The product of this command is not meant to be distributed! The access can be revoked after 30 minutes.

## Bundling your game once it's ready an can be released: how-to

When your game is finished, polished, test... You are ready to go, you can share it and distribute over the Internet! To do so, first you would need to create an account on the [Kata.games platform](https://kata.games), register if you haven't yet, it is free!

Once you have your account, log in using the web interface (top right widgets on the landing page).
This will let you access to *Advanced options related to your Kata.games account*.

Once you have downloaded you key you can copy it to any folder on your hard drive. Copy/move it to make things convenient for you.

Go to the directory parent to your project (one step below the project's root folder), then if my account name is `goku3` for example I would type this command:

    katasdk bundle goku3.key folder/

## Run again existing bundles (tests, or release)

If your wbundle already exists but you want to run it again,
you can use this command:

    katasdk serve folder/

Click on the third button: **"Request a Dev Demo key (KataSDK)""**
you get one unique DevKey per account but you can download this file as many times as needed.

If you need further assistance, you can [join our Discord community](https://discord.gg/3NFfvHAt44)
and ask anything. You can also contact the support: [support@kata.games](mailto:support@kata.games) Have fun coding for the Web!
