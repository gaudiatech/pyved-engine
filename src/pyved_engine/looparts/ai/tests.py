from .NorrecBrain import NorrecBrain


def run_test():
    npcs2class = {
        'norrec': NorrecBrain
    }
    curr_npc_name = 'norrec'
    pnj_courant = npcs2class[curr_npc_name]()  # build npc instance
    CODE_EXIT = 'Q'

    # print tutorial
    print("simulateur de dialogue, à tout moment vous pouvez saisir '" + CODE_EXIT + "' pour quitter")
    print("le dialogue commence...")
    print('\n' + '-'*44)

    # loop
    SYM_PROMPT = '>>> '
    pnj_courant.say_something()
    saisie = input(SYM_PROMPT)
    while saisie != CODE_EXIT:
        pnj_courant.entree_info(saisie)
        pnj_courant.say_something()
        saisie = input(SYM_PROMPT)
    print('done!')
