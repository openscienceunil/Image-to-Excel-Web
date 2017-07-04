# Image-to-Excel

## Description
Avec Image-to-Excel, convertissez un tableau sous format image en tableau Excel ou interagissez avec pour créer des graphiques à bar directement sur la page web.

## Fonctionnalités
Cette version est un prototype qui ne fonctionne qu'avec les deux images dans le dossier img.

Actuellement, il est possible de télécharger le Tableau directement sur le bureau.
Il est aussi possible d'analyser ce graphique pour créer un barplot (graphique à bar).

## Interface
La page d'accueil permet de choisir un fichier image puis renvoie sur une nouvelle page avec le tableau affiché.

Depuis cette nouvelle page, il est possible d'analyser le tableau pour créer un barplot, de le télécharger en format Excel ou d'analyser une autre image 

## Dépendances
Cette application interagit avec un script python. 
Python 2.7 doit être installé.

Son installation est décrite dans la section "Installation" ci-dessous

Python utilise les packages suivants (déjà contenus dans le code, aucune installation nécessaire):
- pylab, 
- pickle, 
- sys,  
- os,
- scipy.ndimage,
- xlwt,
- Tkinter,
- tkFileDialog, 
- PIL, 
- subprocess, 
- flask,
- werkzeug,
- json

## Installation (Windows)
- Python 2.7

    Allez sur https://www.python.org/downloads/ et suivez l'aide d'installation.
  
## Auteurs
Cette application a été créée par Xavier BARROS dans le cadre du séminaire de Visualisation de donnée sous la supervision d'Isaac PANTE lors du semestre de printemps 2017 à l'UNIL (Université de Lausanne).
