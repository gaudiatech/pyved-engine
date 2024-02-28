import pyved_engine as pyv

pyv.bootstrap_e()


# aliases
StdCard = pyv.tabletop.StandardCard
PokerHand = pyv.tabletop.PokerHand
pygame = pyv.pygame


# ----------------- debug strength of cards ------------------
# pl_cards = [
#     StdCard('8d'),
#     StdCard('3s'),
# ]
# dealer_cards = [
#     StdCard('5h'),
#     StdCard('Th'),
# ]
# shared_cards = [
#     StdCard('4s'),
#     StdCard('Qh'),
#     StdCard('Kh'),
#     StdCard('Kd'),
#     StdCard('As')
# ]
# dhand = pyv.tabletop.find_best_ph(dealer_cards+shared_cards)
# phand = pyv.tabletop.find_best_ph(pl_cards+shared_cards)
# print(dhand, '\n', phand)
# print(dhand.value, '\n', phand.value)
# print(phand.value > dhand.value)
# import sys
# sys.exit(0)


# OMEGA_SYM = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')  OMEGA_SUIT = ('c', 'd', 'h', 's')
lcards = [
    StdCard('Tc'),
    StdCard('Jc'),
    StdCard('Qc'),
    StdCard('Kc'),
    StdCard('Ac'),
]
# print(lcards[-1].numeric)

p_hand = pyv.tabletop.PokerHand(lcards)
str_fulsh = p_hand.is_royal()  # p_hand.is_straight() and p_hand.is_flush()
# print(' ---', str_fulsh)

# print(p_hand)
# print(p_hand.value)

# - le chargement des assets se fait comme ceci:
spr_sheet = pyv.gfx.JsonBasedSprSheet('cartes')
my_assets = dict()
for card_cod in StdCard.all_card_codes():
    y = PokerHand.adhoc_mapping(card_cod[0]).lstrip('0') + card_cod[1].upper()  # convert card code to path
    my_assets[card_cod] = spr_sheet[f'{y}.png']

print()
print('*'*48)
print('[ Instructions: press space to randomize cards dealt, ESC key to quit ]')
print()
print('The strength of your hand now= ', p_hand.value)


class MaquetteJc(pyv.GameTpl):
    def list_game_events(self):
        return None

    def get_video_mode(self):
        return 2

    def update(self, infot):
        global lcards, p_hand
        # - event detection facon pygame
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    # new draw of cards
                    lcards = [pyv.tabletop.StandardCard.at_random() for _ in range(5)]
                    p_hand = PokerHand(lcards)
                    print('The strength of your hand now= ', p_hand.value)
                elif e.key == pygame.K_ESCAPE:
                    self.gameover = True

        # - maj graphique
        pyv.get_surface().fill('darkgreen')
        images = list()
        for card_obj in p_hand:
            images.append(my_assets[card_obj.code])

        for k, img in enumerate(images):
            pyv.get_surface().blit(img, (32+k*55, 256) )
        pyv.flip()


g = MaquetteJc()
g.loop()
