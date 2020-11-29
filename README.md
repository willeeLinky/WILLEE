![Image](logos/LogoFinalWILLEE.png?raw=true)

# Bienvenue chez WILLEE, l'afficheur temps réel de consommation électrique Linky !

WILLEE est un programme simple et gratuit, qui collecte et affiche en temps réel la consommation de votre compteur électrique Linky.
Voilà par exemple <a href="./screenshots/captureWILLEEFrontend.PNG" target="_top">ce qu'il affiche</a>.
Les figures sont modulables (on peut cliquer, zoomer...).

WILLEE est codé en langage Python et hébergé sur une carte Raspberry Pi.

## Matériel
* **Une Raspberry Pi 0, 3, ou 4 avec interface GPIO :** Personellement j'ai utilisé WILLEE sur une Pi3B puis une Pi0 WH ([acheter ici par exemple](https://www.kubii.fr/cartes-raspberry-pi/2076-raspberry-pi-zero-wh-kubii-3272496009394.html)).
* **Une alimentation pour la Raspberry Pi:** ([acheter ici par exemple](https://www.kubii.fr/14-chargeurs-alimentations-raspberry/1639-alimentation-raspberry-pi-5v-25a-pour-raspberry-pi-3-couleur-blanche-kubii-640522710911.html)).
* **Une carte SD 16Go ou plus** (facile à trouver).
* **[optionnel] Un boitier pour la raspberry:**  [acheter ici par exemple](https://www.kubii.fr/boitiers-et-supports/1833-boitier-pi-zero-modmypi-kubii-3272496006799.html#/171-couleur-blanc).
* **... ou alors un kit Raspberry Pi** comme [celui-ci](https://www.kubii.fr/raspberry-pi-microbit/2079-kit-pi-zero-wh-kubii-3272496009523.html), qui a la bonne idée de rassembler les éléments ci-dessus, plus des adaptateurs HDMI et USB. De plus, la carte SD arrive prête à l'emploi. [Celui-ci](https://www.kubii.fr/kits-raspberry-pi/2078-kit-pi-zero-v13-kubii-3272496009516.html) est bien aussi, puisque 2x moins cher que le présédent, mais il faut être équipé pour souder les connecteurs soi-même.
* **Un adaptateur d'impédance :** Se présente sous la forme d'une petite carte ([acheter ici](https://www.tindie.com/products/Hallard/pitinfo/)), ce que j'ai choisi, ou d'un optocoupleur à souder soi-même ([plus d'info ici](https://hallard.me/pitinfov12/)).
* **Un petit câble** pour connecter la Raspberry Pi au compteur Linky.
* **... et un compteur Linky...** 

## Prérequis
* **Raspberry Pi OS (Raspbian) est installé** sur la carte SD. Cela peut-être réalisé avec [NOOB](https://www.raspberrypi-france.fr/guide/installer-raspbian-raspberry-pi/) pour quelqu'un qui débute, mais je conseille d'installer la version [Raspberry Pi OS Lite](https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit) pour quelqu'un de plus éclairé, en particulier en cas d'utilisation d'une Raspberry Pi 0. Ecran/clavier/souris peuvent être requis pour la première configuration (pour l'accès à internet par exemple), et éventuellement les adaptateurs mini-HDMI vers HDMI et mini-USB vers USB. Penser aussi à changer le mot de passe, par sécurité. A terme, je conseille d'autoriser l'accès par SSH, voire par VNC si besoin.
* **L'adapteur d'impédance est bien branché sur la Raspberry Pi.**
* **L'adapteur d'impédance est bien connecté au compteur Linky.** 
* **La Raspberry Pi est correctement connectée à internet (Wifi).**
* **L'heure de la Raspberry Pi est juste.** (vous êtes au moins sur le bon fuseau horaire).
	* Pour vérifier : timedatectl
	* Pour modifier : sudo dpkg-reconfigure tzdata
* Si tout est branché correctement comme sur le schéma dessous, c'est parti !

![Image](screenshots/schemaMontage.png?raw=true)

## Etape 1 : Environnement logiciel
Mettre à jour la Raspberry Pi et installer quelques paquets :

	sudo apt-get update
	sudo apt-get upgrade #cela peut prendre un peu de temps
	sudo apt-get install git python3 python3-pip picocom

## Etape 2 : Configuration des ports GPIO
Il faut préalablement permettre à la Raspberry Pi de lire les signaux du compeur Linky ([selon cette source](https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3-4/)) en désactivant par la même occasion le bluetooth. Pour ça, taper :

	sudo systemctl stop serial-getty@ttyAMA0.service
	sudo systemctl disable serial-getty@ttyAMA0.service
	sudo systemctl stop serial-getty@ttyS0.service
	sudo systemctl disable serial-getty@ttyS0.service
	echo 'enable_uart=1' | sudo tee -a /boot/config.txt
Ensuite, dans le fichier `/boot/cmdline.txt`, on doit voir quelque chose du genre : 

	dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes root wait. 

Retirer la partie `console=serial0,115200` de la ligne en question (utiliser `sudo nano /boot/cmdline.txt` ; *CTRL+O* pour sauvegarder ; *CTRL+X* pour quitter).
Rebooter pour prendre en compte tous les changements :

	sudo reboot
Essayez maintenant de lire les infos du compteur grâce au petit logiciel *picocom* installé dans l'étape 1 (ctrl+A+X pour quitter).

	sudo  picocom -b 1200 -d 7 -p e -f n /dev/ttyS0 # Pour quiter : ctrl+A+X

Vous devez voir s'afficher en temps réel du texte, comme suit. Il s'agit des *téléinformations* de votre compteur Enedis ([ici pour plus d'info](https://www.enedis.fr/sites/default/files/Enedis-NOI-CPT_02E.pdf)).
![Image](screenshots/picocom.png?raw=true)

Si vous obtenez quelque chose de similaire, vous pouvez passer à l'étape suivante !
Dans le cas contraire, vérifiez les branchements.

## Etape 3 : Installation du projet
Créer un dossier appelé WILLEE et se placer dedans:

	mkdir WilleeProject 
	cd WilleeProject
Cloner le projet et se placer dans le dossier.

	git clone https://github.com/willeeLinky/WILLEE.git
	cd WILLEE
Installer les librairies python (cela peut prendre du temps). L'usage du `sudo` est requis pour l'étape 4 (optionnelle).

	sudo pip3 install -r requirements.txt
Lancer le *backend* de WILLEE, qui remplit la base de données :

	sudo python3 backend.py & 
	
La base de données est créée automatiquement, ainsi que les tables (taper `ls -lah` pour la voir dans le dossier).
Lancer le *frontend* qui génère la page web :
	
	sudo python3 frontend.py & 
## Et voilà ! 
WILLEE va accumuler des donnée à raison d'environ ~600Mo/an.
Vous pouvez visualiser la page web depuis la Raspberry Pi ou un autre équipement connecté au réseau local en tapant "*[IP de la Raspberry Pi]:8050*" dans un navigateur.
Pour connaitre l'IP : `ip addr` dans l'invité de commande, puis chercher quelque chose du genre "*inet 192.168.1.2/24*".

Il est normal que rien ne soit affiché sur le second graphe de WILLEE : les données correspondantes sont prises à minuit. Il faut donc attendre "deux minuits" pour que WILLEE ait pu faire la soustraction sur deux données prises à minuit et ainsi afficher la consommation de la journée correspondante.

![Image](screenshots/captureWILLEEFrontend.PNG?raw=true)

## Etape 4 : Faire fonctionner WILLEE avec *systemd* [optionnel]
Pour améliorer les choses, on peut laisser le soin à "systemd" de les deux programmes de WILLEE, plutôt que de les lancer dans le shell. Après tout, systemd est le gestionanaire de service pour Linux.
On va donc commencer par stopper le backend et le frontend de WILLEE. Taper `ps -a` pour trouver les scripts Python en cours d'exécution, et les arrêter avec `kill [PID]`.
Ensuite, copier les fichiers `*.service` sous `/etc/systemd/system` :
	
	sudo cp /home/pi/WilleeProject/WILLEE/Backend.service /etc/systemd/system/.
	sudo cp /home/pi/WilleeProject/WILLEE/Frontend.service /etc/systemd/system/.
Comme le montrer la 7e ligne des fichiers `Backend.service` et `Backend.service`, ceux-ci lancent les scripts `backend.py` et `frontend.py` en supposant qu'ils sont enregistrés sous `/home/pi/WilleeProject/WILLEE/`. Il faut adapter le contenu de ces fichiers si vous n'utilisez pas la même organisation que ce tutoriel.

Autoriser les fichiers system à s'exécuter au démarrage :

	sudo systemctl daemon-reload
	sudo systemctl enable Backend
	sudo systemctl enable Frontend

Vérifier l'état avec `status` :

	sudo systemctl status Backend
	sudo systemctl status Frontend

Les fichiers deviennet alors des services, qui seront lancés au démarrage de la Raspberry. Il est aussi possible de lancer/arrêter/redémarrer les fichiers "à la main", en reprenant la commande ci-dessus et en remplaçant `status` par `start` ou `stop` ou `reload`.

## Sources et projets similaires
A venir.
    
[Editeur markdown](https://stackedit.io/app#)
