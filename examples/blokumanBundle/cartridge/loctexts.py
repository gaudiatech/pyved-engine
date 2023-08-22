_str_repo = dict()


def init_repo(lang):
    global _str_repo
    from .labels import Labels

    # ---------------------------
    #  Version anglaise
    # ---------------------------
    if lang=='en':
        _str_repo[Labels.PoidsTotal] = 'TOTAL WEIGHT'
        _str_repo[Labels.UtiliteTotale] = 'UTILITY'

        _str_repo[Labels.Minage1] = 'Donating hashpower to the ludo.store'
        _str_repo[Labels.Minage2] = 'Please wait for a short moment...'

        _str_repo[Labels.NomJoueurAnonyme] = 'Guest'
        _str_repo[Labels.SensLogin] = 'Please identify yourself'

        _str_repo[Labels.CanCreateAcc] = "No account yet? Sign up via http://ludo.store"
        _str_repo[Labels.InciteLudoStore] = "It's easy, fast and 100% free!"

        _str_repo[Labels.Utilisateur] = 'User'
        _str_repo[Labels.Invite] = 'Guest'
        _str_repo[Labels.Solde] = 'Balance'

        _str_repo[Labels.OpenBrowser] = 'Open in default browser'

        _str_repo[Labels.WindowCaption] = 'Bag&Win: the game'

        _str_repo[Labels.Connexion] = 'Do login'

        _str_repo[Labels.MenuGridGame] = 'Easy mode'
        _str_repo[Labels.MenuDefi] = 'Take the challenge'
        _str_repo[Labels.MenuTuto] = 'Tutorial'
        _str_repo[Labels.MenuEntrainement] = 'Training'
        _str_repo[Labels.MenuQuitter] = 'Quit'

        _str_repo[Labels.NoTraining] = 'Training mode\'s unavailable in this prototype. ESC to go back to the menu'

        _str_repo[Labels.CompteRequis] = 'You need to login first'
        _str_repo[Labels.CoutDefi] = 'costs 10 mGold per try'

        _str_repo[Labels.RetourArr] = 'Go back'

        _str_repo[Labels.CannotLogin] = "ERROR: Credentials are not accepted by the server!"

        _str_repo[Labels.WordLogin] = 'ACCOUNT NAME-'
        _str_repo[Labels.WordPassword] = 'PASSWORD-'

        _str_repo[Labels.EndEasyWin] = 'Congratulations! You win'
        _str_repo[Labels.EndEasyLoose] = 'Game over! You loose'

        _str_repo[Labels.EndChallenge1] = 'Time elapsed'
        _str_repo[Labels.EndGameAction] = "Press [ENTER] to go back to the menu"

        return

    # ---------------------------
    #  Version française
    # ---------------------------
    _str_repo[Labels.PoidsTotal] = 'POIDS TOTAL'
    _str_repo[Labels.UtiliteTotale] = 'UTILITE'

    _str_repo[Labels.Minage1] = 'Contribution ludo.store'
    _str_repo[Labels.Minage2] = 'Veuillez patienter durant le minage...'

    _str_repo[Labels.NomJoueurAnonyme] = 'Invite(e)'
    _str_repo[Labels.SensLogin] = 'Selection du compte-joueur'

    _str_repo[Labels.CanCreateAcc] = "Si besoin de creer compte: http://ludo.store"
    _str_repo[Labels.InciteLudoStore] = "Facile, rapide, 100% gratuit!"

    _str_repo[Labels.Utilisateur] = 'Profil'
    _str_repo[Labels.Invite] = 'Invite'
    _str_repo[Labels.Solde] = 'Solde'

    _str_repo[Labels.OpenBrowser] = 'Ouvrir dans votre navigateur'

    _str_repo[Labels.WindowCaption] = 'Bag&Win: le jeu'

    _str_repo[Labels.Connexion] = 'S\'authentifier'
    _str_repo[Labels.MenuDefi] = 'Jouer en tournoi'

    _str_repo[Labels.MenuGridGame] = 'Mode facile'
    _str_repo[Labels.MenuTuto] = 'Tutoriel'
    _str_repo[Labels.MenuEntrainement] = 'Entrainement'
    _str_repo[Labels.MenuQuitter] = 'Quitter'

    _str_repo[Labels.NoTraining] = 'mode Entrainement indisponible dans cette maquette. ESC pour revenir au menu'

    _str_repo[Labels.CompteRequis] = 'Il te faut un compte'
    _str_repo[Labels.CoutDefi] = 'coute 10 mGold par essai'

    _str_repo[Labels.RetourArr] = 'Retour arriere'

    _str_repo[Labels.CannotLogin] = 'ERREUR: Identifiants refuses par le serveur!'

    _str_repo[Labels.WordLogin] = 'NOM COMPTE-'
    _str_repo[Labels.WordPassword] = 'MOT DE PASSE-'

    _str_repo[Labels.EndEasyWin] = 'Bravo! Vous gagnez'
    _str_repo[Labels.EndEasyLoose] = 'Game over! Vous perdez'

    _str_repo[Labels.EndChallenge1] = 'Temps ecoule'
    _str_repo[Labels.EndGameAction] = "Pressez [ENTREE] pour revenir au menu"


def tsl(cle):
    global _str_repo
    return _str_repo[cle]
