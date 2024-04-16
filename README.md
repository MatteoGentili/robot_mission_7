# Robot Mission, Groupe 7
Self-organization of robots in a hostile environment


## Groupe
- FOSSAT Théotime
- GENTILI Matteo
- PALARIC Aymeric
- PETIT Alexandre

## Objectif
L'objectif de ce projet est de simuler un environnement hostile dans lequel des robots doivent se déplacer pour accomplir une mission. Les robots doivent s'organiser pour transformer et déplacer des déchets dans une grille pour les recycler.

## Step 1 : Pas de communication entre les agents
Dans un premier temps, les robots ne peuvent pas communiquer entre eux. Ils executent donc leur tâche "en concurrence" les uns avec les autres.

Nous avons doté chaque robot de la `knowledge` suivante :
- `wastes` : la liste des déchets et de leur position
- `robots` : la liste des robots et de leur position
- `inventory` : la liste des déchets que le robot transporte
- `pos` : la position du robot
- `color` : la couleur du robot
- `right\left border` : la position de la limite de la zone de travail du robot
- `radioactivity` : la carte de radioactivité de la grille
- `radioactivity_limit` : la limite de radioactivité tolérée par le robot (respectivement 1/3, 2/3, et infinie)
- (robot rouge uniquement) `disposal_zone` : la position de la zone de dépose finale

Les robots verts et jaunes ont les mêmes fonctions `deliberate` : ils cherchent le déchet de leur couleur le plus proche et se déplacent pour le porter jusqu'à en avoir 2, auquel cas ils se dirigent vers leur frontière de zone de travail respective pour les déposer en les transformant en un déchet de couleur "supérieure".
Lorsque les déchets sont ramassés, ils sont retirés de l'environnement.

Les robots rouges ont une fonction `deliberate` différente : ils cherchent le déchet le plus proche et se déplacent pour le transporter directement dans la zone de dépose finale.

Une fois l'action du robot effectuée, le model lui renvoie une image de la grille après l'action réalisée en lui donnant la position des déchets et des robots.

## Step 2 : Communication entre les agents

**Analyse du système de communication :**

Broadcast par couleur : Chaque robot ne communique qu'avec des robots de la même catégorie de couleur. Cela réduit le trafic de communication et évite les interférences inutiles entre les robots qui ne partagent pas les mêmes objectifs.

**Sélection des déchets :**

Le premier robot choisit le déchet le plus proche de sa couleur.
Les robots suivants choisissent les déchets les plus proches, en excluant ceux déjà ciblés par d'autres robots. Cela maximise l'efficacité en évitant la redondance et en minimisant les trajets.

**Utilisation des performatifs ARGUE, COMMIT et CANCEL :**

ARGUE est utilisé par un robot pour indiquer qu'il détient déjà un déchet. Cela pourrait être interprété comme une demande aux autres robots de ne pas cibler le même type de déchet si cela n'est pas nécessaire.
COMMIT est utilisé par un autre robot pour indiquer qu'il est prêt à transférer un déchet, ce qui entraîne l'annulation du ARGUE par le premier robot qui envoie à tous les autres robots un message CANCEL. Ceci est essentiel pour la synchronisation des actions entre les robots.
Transfert de déchets : Les robots se rejoignent pour transférer les déchets de l'un à l'autre, afin de maximiser le nombre de déchets recyclés.

## Run
Le code utilise plusieurs bibliothèques, notamment pour la gestion de l'environnement et des agents. Elles sont regroupées dans le fichier `requirements.txt` et peut être exécuté par la commande : 
```pip install -r requirements.txt```.

Pour lancer la simulation, il suffit de lancer le script `run.py` avec la commande :

```python -m run --green_robot 3 --yellow_robot 3 --red_robot 3 --nb_wastes 16 --grid_width 21 --grid_height 3 --opti True```. 
Cela va lancer le programme avec les paramètres choisis. La commande ci-dessus montre les paramètres par défaut, qui fonctionne aussi simplement avec la commande `python -m run`. Les paramètres peuvent être choisis indépendamment, ceux qui ne sont pas explicité dans la commande seront mis à leur valeur par défaut. Les paramètres sont les suivants :
- `green_robot` : le nombre de robots verts
- `yellow_robot` : le nombre de robots jaunes
- `red_robot` : le nombre de robots rouges
- `nb_wastes` : le nombre de déchets sur la grille
- `grid_width` : la largeur de la grille
- `grid_height` : la hauteur de la grille
- `opti` : si True, lance la simulation avec des robots communiquants, sinon sans communication

Durant la simulation, une fenêtre s'ouvre montrant l'état actuel de la grille.

2 images sont aussi générées dans le dossier figures, dont les noms seront suivis du suffixe `_opti` si la simulation a été lancée avec des robots communiquants, et `_nonopti` sinon :
- `wastes_remaining.png` : le nombre de déchets restants sur la grille
- `wastes_fullrecycled.png` : le nombre de déchets recyclés par les robots rouges

## Résultats
Les résultats de la simulation sont stockés dans le dossier `figures`. Les images générées montrent le nombre de déchets restants sur la grille et le nombre de déchets recyclés par les robots rouges.
On peut notamment voir des différences notables entre les simulations avec et sans communication :
- Avec communication, la simulation a tendance à être plus longue, mais les robots sont plus efficaces et recyclent plus de déchets : il ne reste à la fin que le nombre minimal de déchets.
- Sans communication, la simulation est plus rapide, mais les robots sont moins efficaces et il reste plus de déchets à la fin.
