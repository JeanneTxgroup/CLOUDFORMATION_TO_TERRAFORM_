Pour travailler sur ces fichiers, il faut avoir WSL (Windows Subsystem for Linux) et Ubuntu sur VS Code.

Etape 1 : Installer WSL

Ouvrir PowerShell sur Windows.
Taper la commande :
wsl --install
Redémarrer la VM si besoin.
WSL permet d’avoir Linux directement sur Windows.

Etape 2 : Installer Ubuntu

Ouvrir le Microsoft Store.
Chercher et télécharger Ubuntu 24.04.1 LTS.
Ouvrir Ubuntu. Un terminal Linux s’ouvrira.
Mettre à jour Ubuntu avec :
sudo apt update && sudo apt upgrade -y
Cela installe toutes les dernières mises à jour.

Etape 3 : Configurer VS Code

Ouvrir VS Code.
Aller dans Extensions (Ctrl+Shift+X).
Chercher WSL et installer.
En bas à gauche, cliquer sur le bouton >< pour Connect to WSL.
Une nouvelle fenêtre VS Code s’ouvre directement dans Ubuntu.
Vous pouvez maintenant ouvrir n’importe quel dossier ou créer un projet Terraform.

Etape 4 : Installer les outils
Dans Ubuntu, installer les logiciels nécessaires :
sudo apt install git python3 python3-pip -y
Git pour le code, Python et pip pour les scripts.

Etape 5 : Tutoriel complet
Pour un tutoriel plus détaillé, il est disponible sur mon Drive.
