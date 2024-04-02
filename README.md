# Robot Mission, Groupe 7
Self-organization of robots in a hostile environment


## Groupe
- GENTILI Matteo
- PETIT Alexandre
- FOSSAT Théotime
- PALARIC Aymeric

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
- `border` : la position de la limite de la zone de travail du robot
- `radioactivity` : la carte de radioactivité de la grille
- `radioactivity_limit` : la limite de radioactivité tolérée par le robot (respectivement 1/3, 2/3, et infinie)
- (robot rouge uniquement) `disposal_zone` : la position de la zone de dépose finale

Les robots verts et jaunes ont les mêmes fonctions `deliberate` : ils cherchent le déchet de leur couleur le plus proche et se déplacent pour le porter jusqu'à en avoir 2, auquel cas ils se dirigent vers leur frontière de zone de travail respective pour les déposer en les transformant en un déchet de couleur "supérieure".
Lorsque les déchets sont ramassés, ils sont retirés de l'environnement. Lorsqu'ils sont déposés, de nouveaux sont créés.

Les robots rouges ont une fonction `deliberate` différente : ils cherchent le déchet le plus proche et se déplacent pour le transporter directement dans la zone de dépose finale.

## Run
Pour lancer la simulation, il suffit de lancer le script `run.py` avec la commande :
`python -m run --green_robot 3 --yellow_robot 3 --red_robot 3 --NbWaste 16 --GridLen 21 --GridHeight 3 --nsteps 10`. 
Cela va lancer le programme avec les paramètres choisis. La commande ci-dessus montre les paramètres par défaut, qui fonctionne aussi simplement avec la commande `python -m run`.
Le paramètre _GridLen_ doit être un multiple de 3.
Durant la simulation, une fenêtre s'ouvre montrant l'état actuel de la grille. De plus, de nouveaux déchets peuvent apparaître aléatoirement sur la grille avec une probabilité de 0.15.

2 images sont aussi générées :
<!-- - `nbwastes_carried.png` : le nombre de déchets transportés par chaque robot -->
- `wastes_remaining.png` : le nombre de déchets restants sur la grille
- `wastes_fullrecycled.png` : le nombre de déchets recyclés par les robots rouges