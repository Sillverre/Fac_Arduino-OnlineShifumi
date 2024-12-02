
Branchements:

Joystick : 
	.GND -> GND
	.5V -> 5V
	.VRx -> A0
	.VRy -> A1
	.SW -> 13

LCD : 
	.VSS -> GND
	.VDD -> 5V
	.VO -> Potentiomètre Milieu
	.RS -> 12
	.RW -> GND
	.E -> 11
	.D4 -> 5
	.D5 -> 4
	.D6 -> 3
	.D7 -> 2
	.A -> Résistance -> 5V
	.K -> GND

Potentiomètre :
	.Milieu -> LCD VO
	.Bas Gauche -> 5V
	.Bas Droite -> GND

Déroulement d'une partie:

Une partie se déroule en plusieurs manches définies par le joueur serveur.
Le joueur serveur lance le serveur, les autres joueurs s'y connectent. Les identifiants des joueurs leurs sont assignés par leur ordre de connexion, avec le joueur serveur étant le joueur 0.
Quand demandé, chaque joueur oriente son joystick afin de choisir un signe (roc/papier/ciseaux).
Broches orientés vers le haut, les signes sur le joystick sont : roc à droite (2), papier en bas (0) et ciseaux à gauche (1).
Si un joueur ne joue pas lors d'une manche, il est compté comme perdant.
Pendant la phase de choix, le signe choisi par le joueur sera indiqué sur l'écran LCD par son initiale.

Une fois que tout les choix sont faits, le terminal du joueur serveur affiche les choix de chaque joueur, comment ils ont été interprétés selon les règles, et par conséquent les gagnants de la manche.
Chaque joueur qui gagne une manche obtient 1 point.
Chaque joueur reçoit alors sur son écran LCD l'id du joueur qui gagne la manche.

A la fin de toutes les manches, le joueur avec le plus haut score reçoit sur son écran LCD un message de félicitations, et les autres un message de défaite, avec l'id du joueur gagnant.





Commande à lancer depuis le terminal:

-coté serveur
python3 shifumi.py -s [IPlocaleServer] [PortSocket] [chemin_du_port_série] [nb_joueurs] [nb_manches]

Le chemin du port série sur lequel est branché l'arduino dépend du système d'exploitation utilisé, et doit être connu par l'utilisateur.
L'IP locale est votre IP au sein de votre réseau local, donc sera très souvent de la forme 192.168.X.X .

-coté client
python3 shifumi.py [IPPublicServer] [PortSocket] [chemin_du_port_série] [nb_joueurs] [nb_manches]

IPPublicServer est l'IP du routeur du joueur serveur. Par conséquent, le joueur serveur doit créer des règles NAT qui redirige le traffic dirigé vers le PortSocket du routeur vers sa machine, ce qui se fait en paramétrant sa box internet.