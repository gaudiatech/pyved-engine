from . import glvars


kengi = glvars.katasdk.pyved_engine


Labels = kengi.e_struct.enum(
    'PoidsTotal',
    'UtiliteTotale',

    'Minage1',  # titre affiché pr le mode taxe
    'Minage2',  # phrase attente

    'WindowCaption',
    'Utilisateur',
    'Solde',
    'Invite',

    'NomJoueurAnonyme',

    'EndEasyWin',
    'EndEasyLoose',

    'EndChallenge1',

    'EndGameAction',  # pr indiquer ce que lutilisateur doit faire

    'SensLogin',  # titre mode login

    'WordLogin',
    'WordPassword',

    'OpenBrowser',
    'CanCreateAcc',  # phrase pr dire tu peux taper les infos!
    'InciteLudoStore',

    'CannotLogin',
    'Connexion',

    'MenuDefi',

    'MenuGridGame',  # nom bouton pour exec. grid game

    'MenuTuto',
    'MenuEntrainement',
    'MenuQuitter',

    'RetourArr',

    'NoTraining',

    'CompteRequis',
    'CoutDefi'
)
