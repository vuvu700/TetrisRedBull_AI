
## pour la V1: 

s'inspire en partie de [ce repo git](https://github.com/truonging/Tetris-A.I) pour ne pas reinventer la roue.

## stack technique
on vas utiliser le meme principe de states avec des features calculées sur la grille (on ne donne pas la grille direct)
on vas par contre utiliser de la planification car on vas avoir une piece en memoire + on connais la prochaine qui est jouable
les combinaisons de planif sont donc:
 - place current (-> holding next, mem = mem)
    - place next (-> mem = mem)
    - place mem (-> mem = next)
 - place mem (-> holding next, mem = current)
    - place next (-> mem = current)
    - place mem (-> mem = next)
rq: pour le premier coup a jouer, on met direct la piece en memoire (comme ca on a toujour une piece en mem)
 donc on ne peux pas utiliser la memoire pour le premier coup
 de plus pour certaines strategies a voire pour blocker la piece gold en memoire

observations:
 - la next -> elle est toujours distribuée a la meme rotation r0 ! 
    -> on peux donc se contenter de regarder la couleur pour connaitre la piece

### la stack IA
je vais utiliser du Deep TD-Learning pour estimer la value function avec deux models, avec une priorized experiance replay pour diminuer les bias. 

Les etats seront décris par (total_height, bumpiness, holes, line_cleared, y_pos, pillar) provenant du repo d'inspiration, et voir pour rajouter en plus le nb de blocks de la grille par ligne et colones.




## deroulé d'une game:
 - avant le début de la partie (pendent le décompte par exemple):
   - screen de l'ecran -> detecter le btn pause, le cadre de score, le logo redbull (avec img)
   - determiner a partir de ca le rect de la grille et le rect du next (rects précis sans bordures)
   - recup la next piece (ca sera donc la premiere mem piece)
 - a partir du debut de la game (-> quand le go au milieu s'efface):
  - read le next (ca sera donc la premiere current piece)
  - metre en memoire => (on connais la piece en mem et la piece current)
  - jouer la partie normalement !
 - a la fin de la partie (soit win (avec timer interne), soit loose arrive pas a detect la nex piece)
  - on lache tout !