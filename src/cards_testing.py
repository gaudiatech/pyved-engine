import katagames_engine as kengi

kengi.bootstrap_e()


# aliases
StdCard = kengi.tabletop.StandardCard
PokerHand = kengi.tabletop.PokerHand
pygame = kengi.pygame


# init cartes & tirage
# lcards = [kengi.tabletop.StandardCard.at_random() for _ in range(5)]

#     OMEGA_SYM = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')  OMEGA_SUIT = ('c', 'd', 'h', 's')
lcards = [
    StdCard('Tc'),
    StdCard('Jc'),
    StdCard('Qc'),
    StdCard('Kc'),
    StdCard('Ac'),
]
print(lcards[-1].numeric)

p_hand = kengi.tabletop.PokerHand(lcards)
str_fulsh = p_hand.is_royal()  # p_hand.is_straight() and p_hand.is_flush()
print(' ---', str_fulsh)

print(p_hand)
print(p_hand.value)

# - le chargement des assets se fait comme ceci:
spr_sheet = kengi.gfx.JsonBasedSprSheet('cartes')
my_assets = dict()
for card_cod in StdCard.all_card_codes():
    y = PokerHand.adhoc_mapping(card_cod[0]).lstrip('0') + card_cod[1].upper()  # convert card code to path
    my_assets[card_cod] = spr_sheet[f'{y}.png']


class MaquetteJc(kengi.GameTpl):

    def enter(self, vms=None):
        kengi.init(2)
        self._manager = kengi.get_ev_manager()
        self._manager.setup()
        self.scr_ref = kengi.get_surface()

    def update(self, infot):
        global lcards, p_hand
        # - event detection facon pygame
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    # new draw of cards
                    lcards = [kengi.tabletop.StandardCard.at_random() for _ in range(5)]
                    p_hand = PokerHand(lcards)
                elif e.key == pygame.K_ESCAPE:
                    self.gameover = True

        # - maj graphique
        self.scr_ref.fill('darkgreen')
        images = list()
        for card_obj in p_hand:
            images.append(my_assets[card_obj.code])

        for k, img in enumerate(images):
            self.scr_ref.blit(img, (32+k*55, 256) )
        kengi.flip()


g = MaquetteJc()
g.loop()
