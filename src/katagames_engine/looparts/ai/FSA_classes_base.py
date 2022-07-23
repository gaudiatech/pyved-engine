

class Transition:
    '''
    classe modélisant la transition dun FSA,
    on suppose que le déclencheur est un mot-clé
    si le déclencheur est repéré dans les info. reçues,
    la transition est déclenchée
    '''
    
    def __init__(self, info_decl, label_etat_suiv ):
        self.declencheur = info_decl
        self.label_etat_suiv = label_etat_suiv

    def est_declenchee(self, info):
        if self.declencheur in info:
            return True
        return False

    def get_label_etat_suiv(self):
        return self.label_etat_suiv


class Etat:
    '''
    classe modélisant un état de FSA,
    un état peut être initial ou terminal
    un état exploite des info. reçues pour déclencher ou non ses transitions
    vers un autre état
    '''

    def __init__(self, label, li_transitions, est_init=False, est_term=False):
        self.label = label
        self.li_transitions = li_transitions
        self.est_init = est_init
        self.est_term = est_term

    def exploite_info(self, info):
        '''retourne le label de l'état suivant OU None,
        selon qu'une transition est déclenchée OU non'''
        if self.est_terminal():
            return None
        for transition in self.li_transitions:
            #print( transition.label_etat_suiv )
            if transition.est_declenchee( info):
                return transition.get_label_etat_suiv()
        return None
        
    def est_terminal(self):
        return self.est_term

    def est_initial(self):
        return self.est_init

    def get_label(self):
        return self.label


class Automate:
    '''
    classe modélisant un FSA pour Finite States Automaton
    concept très utilisé en IA dans les jeux commerciaux,
    malgré sa simplicité c'est la base du comportement des PNJs
    '''

    def __init__(self, li_etats):
        self.etats = dict()
        for etat in li_etats:
            self.etats[etat.get_label() ] = etat

        self.reset()

    def entree_info(self, info):
        '''permet le changement detat '''
        res = self.get_etat_courant().exploite_info(info)
        if res!=None:
            self.label_etat_courant = res

    def get_etat_courant(self):
        return self.etats[self.label_etat_courant]

    def reset(self):
        init_st_trouve = False
        #initialisation de l'etat courant
        for etat in self.etats.values():
            if etat.est_initial():
                if init_st_trouve: #doublon
                    raise Exception("definition FSA non valide, il ne peut y avoir qu'un état initial")
                self.label_etat_courant = etat.get_label()
                init_st_trouve = True




#--- essais definition

s1 =  Etat( 's1', [ Transition( 'hello', 's2') ] , True, False )
s2 = Etat('s2', [ Transition('news','s4') , Transition('bye','s3') ] )
s4 = Etat('s4', [Transition('ok','s2')] )
s3 = Etat('s3', [] , False, True )

fsa_exemple1 = Automate( [s1,s2,s3,s4]  )



# pour tester, on peut interagir avec le FSA directement dans la console python
# (dessiner le FSA sur papier pour bien le comprendre )
# voici la trace de mes propres tests :


# >>> fsa_exemple1.getEtatCourant().estInitial()
# True
# >>> fsa_exemple1.getEtatCourant().getLabel()
#'s1'

# >>> fsa_exemple1.entreeInfo('hello')
# >>> fsa_exemple1.entreeInfo('news')
# >>> fsa_exemple1.getEtatCourant().getLabel()
#'s4'
# >>> fsa_exemple1.entreeInfo('ok')
# >>> fsa_exemple1.getEtatCourant().getLabel()
# 's2'
# >>> fsa_exemple1.entreeInfo('bye')
# >>> fsa_exemple1.getEtatCourant().getLabel()
# 's3'

# >>> fsa_exemple1.entreeInfo('hello')
# >>> fsa_exemple1.entreeInfo('bye')
# >>> fsa_exemple1.entreeInfo('nimporte quoi')
# >>> fsa_exemple1.getEtatCourant().getLabel()
# 's3'
# >>> fsa_exemple1.getEtatCourant().estTerminal()
# True

# >>> fsa_exemple1.reset()
# >>> fsa_exemple1.getEtatCourant().estInitial()
# True

       

              
        

    

    
