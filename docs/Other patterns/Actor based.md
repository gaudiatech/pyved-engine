
# Actor-Based pattern: a short introduction


\[Nota Bene \] this text is only written in french, for now.
Translations will be available soon.

L'idée derrière le *pattern Actor-based* est que le fonctionnement du jeu,
et plus généralement de tous les composants représentés à l'écran, peut être modélisé
via un ensemble d'acteurs qui intéragissent continuellement entre eux.
 
Le *pattern Actor-based* peut être concrétisé via une spécialisation du *pattern Mediator*,
et donc en utilisant une file d'événements centrale.


Pour tester ce *pattern* dans le moteur **Pyv**, rien de plus simple,
il suffit de mémoriser quelques fonctions qui représentent l'API développeur.

!!! warning
    Le pattern Actor-Based étant ajouté très récemment il peut contenir des bugs. Si vous trouvez
	un bug important, merci de bien vouloir l'ajouter à la liste du projet GitHub en créant une "Issue"


En plus des fonctions listées ci-dessous il s'agira pour tout jeu de gérer les événements.
La solution actuellement utilisée est la suivante:

- faire un routage des événements bas-niveau vers des événements définis par vous même,
pour cela on peut accéder à `pyv.evsys0`
- via les acteurs définis un à un, les événements de plus haut niveau sont traités grâce aux fonctions dites
"de comportement" ou "behavior" en anglais.

Pour récupérer des choses importantes par rapport aux évents bas-niveau, on peut utiliser:
- `pyv.evsys0.get()` lister les évenements survenus
- `pyv.evsys0.pressed_keys()` ensemble des touches pressées en ce moment


## 1/ les "core functions"

- `bootstrap_e()` pour initialiser le moteur en tant que tel (faire en sorte que sa logique interne de chargement de modules & pré-chargement de données soit prête à l'emploi)
- `init(mode [, forced_size, wcaption, maxfps])` pour initialiser la partie affichage
- `close_game()` en fin de jeu
- `flip()` en fin de fonction `update` de votre jeu. Fondamentalement: ça permet de synchroniser le contenu de la mémoire RAM avec la mémoire de votre carte graphique


## 2/ les "pattern-specific functions"

- `new_actor(ac_type, local_vars)`
- `del_actor(ac_id)` : retire un acteur du jeu
- `peek(ac_id)` : accède directeremnt aux données d'un acteur
- `trigger(func_name, ac_id, *args)` : déclenche la fonction utilitaire mentionnée, que l'on trouve chez un acteur
- `id_actor(data_chunk)` : rarely used, but can be useful. This allows you to retrieve an actor reference based on the data you access

C'est bien d'avoir des acteurs, encore faut-il qu'ils réagissent à des choses.

- `declare_evs(*args)` en début de jeu, pour indiquer explicitement quels événements votre jeu utilise
- `process_evq()` pour traiter la file des événements en attente
- `post_ev(ev_name, **kwargs)` : kwargs représente la liste des associations `key=value` que vous désirez rajouter à l'événement posté

Si le jeu est plus que basique, il vous faudra des "scènes". Avec le *Actor-Based pattern*, on parle de *worlds*

- `get_world()` effet évident, un world étant représenté simplement par son nom. Le *world* par défaut c'est "default"
- `set_world()` changer de monde va automatiquement ranger tous vos acteurs pour passer à ceux pré-définis dans le monde cible,
à noter qu'aucun acteur n'est supprimé ou ajouté lors d'une transition monde A-> mondeB !
Faites donc attention à quand et comment vos acteurs sont initialisés.

## 3/ la catégorie des "engine utility functions"

Cette catégorie comprend surtout des fonctions de dessins bas-niveau,
on appelle aussi ça "les primitives graphiques".

- `draw_circle`
- `draw_rect`
- `draw_line`
- `draw_polygon` (for more information you may check pygame API reference, as everything is very similar to `pygame` here)
- `new_font_obj`
- `new_rect_obj`
- `suface.fill(color)`
- `surface.blit(autre_surface, pos_xy)`
- `font.render(text, antialias_flag, color [, bgcolor])

En plus de cela on peut avoir accès aux différentes palettes via `pyv.pal.x`,
voir le fichier de définition pour un listing complet des couleurs disponibles:

<https://github.com/pyved-solution/pyved-engine/blob/master/src/pyved_engine/pal.py>
