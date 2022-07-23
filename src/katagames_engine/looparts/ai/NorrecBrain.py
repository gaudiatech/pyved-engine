import random

from .FSA_classes_base import Automate, Etat, Transition

MSG_NEUTRES = [
    "Qu'est-ce que vous m'racontez bon sang ?",
    "J'en sais fichtre rien...",
    "J'vois pas de quoi vous causez, là."
]
MSG_BLOCAGE_NEG = [
    "...",
    "Les aigles ne volent pas avec les pigeons.",
    "Peu importe. Z'êtes pas quelqu'un dont les dires m'intéressent.",
    "Voilà ce qu'on va faire : vous allez là-bas, moi j'reste ici.",
    "Adieu."
]
MSG_BLOCAGE_POS = [
    "On parle, on parle, concentrons-nous plutôt sur l'action !",
    "Suis encor' en train de préparer les armes pour notre prochaine quête...",
    "Ah vous revoilà l'ami !",
    "Hola ! Revoilà le champion !",
    "Suis en train de réunir des pièces pour partir à l'aventure avec vous."
]


class NorrecBrain(Automate):

    def __init__(self):

        self.assoc_etat_msg = {
            'bourru': "Ghhrrn qu'est-ce que c'est... Moi c'est Norrec l'guerrier. J'vous ai déjà vu vous ?",
            'faux_oui': "Ça m'étonnerait ! **non** serait la réponse appropriée, cessez de **mentir**",
            'faux_non': "Ça m'étonnerait ! **oui** serait la réponse appropriée, cessez de **mentir**",
            'suspicieux': "Mentir c'est la pire abomination ! C'est l'attitude reservée aux rats ! Vous êt' d'accord avec moi ?",
            'neutre': "Par ici on aime pas trop les vagabonds surtout ceux qui se promènent en **armure** comme la vôtre.",
            'curieux': "Ah c'est sûr que j'en vois pas souvent des comme ça, **oui** remarquez ce doit être **utile**, **non** ?",
            'demandeur': "Vous dites oui c'est utile ! Comme j'vous comprends. Un bel acier comme ça. J'vous connais pas m'enfin... "
                         + "Vous parlez comme quelqu'un de vrai. "
                         + "Vous pouvez peut-être me **renseigner** sur où acheter une telle armure ?",
            'chaud': "Fantastique ! On dirait bien que je me suis trompé sur vot' compte. "
                     + "Vous êtes bien brave. Si vous avez besoin de recruter un homme fort, ma hache est à vot' service.",
            'froid': "Ah, c'est bien ce que j'pensais : une crapule de plus dans not' ville ! Pouah ! (Norrec crache à vos pieds)"
        }

        # --- définition de 9 états, avec les transitions sortantes respectives
        et1 = Etat('bourru', [
            Transition('oui', 'faux_oui'),
            Transition('non', 'neutre')
        ], True, False)

        et2 = Etat('faux_oui', [
            Transition('mentir', 'suspicieux'),
            Transition('oui', 'neutre')
        ])

        et3 = Etat('suspicieux', [
            Transition('oui', 'neutre'),
            Transition('non', 'froid')
        ])

        et4 = Etat('froid', [], False, True)

        et5 = Etat('neutre', [
            Transition('armure', 'curieux')
        ])

        et6 = Etat('curieux', [
            Transition('non', 'faux_non'),
            Transition('utile', 'demandeur'),
            Transition('oui', 'demandeur')
        ])

        et7 = Etat('faux_non', [
            Transition('mentir', 'suspicieux'),
            Transition('oui', 'demandeur')
        ])

        et8 = Etat('demandeur', [
            Transition('non', 'froid'),
            Transition('oui', 'chaud'),
            Transition('renseigner', 'chaud')
        ])

        et9 = Etat('chaud', [], False, True)

        etats_norrec = [et1, et2, et3, et4, et5, et6, et7, et8, et9]
        super().__init__(etats_norrec)

        self.adhoc_msg = self.assoc_etat_msg[
            self.get_etat_courant().get_label()
        ]

    # redéfinition
    def entree_info(self, info):
        etat_avant = self.get_etat_courant()
        super().entree_info(info)
        nouvel_etat = self.get_etat_courant()

        if nouvel_etat == etat_avant:
            if etat_avant.est_terminal():
                if etat_avant.get_label() == 'froid':
                    self.adhoc_msg = random.choice(MSG_BLOCAGE_NEG)
                else:
                    self.adhoc_msg = random.choice(MSG_BLOCAGE_POS)
                return

            self.adhoc_msg = random.choice(MSG_NEUTRES)
            return

        self.adhoc_msg = self.assoc_etat_msg[nouvel_etat.get_label()]

    def say_something(self):
        print(self.adhoc_msg)
