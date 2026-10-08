# Site de la Maison d'hôtes Tifrit

Site statique en trois langues (français, anglais, allemand), généré par `build.py` à partir de fichiers texte. Aucune base de données, aucun plugin, rien à mettre à jour.

## Pour Rachid : modifier le site

Deux façons, au choix.

**1. L'interface d'administration** (une fois le site hébergé sur Netlify) : ouvrir `tifritecolodge.com/admin/`, se connecter, modifier un texte, un prix ou une date, enregistrer. Le site se reconstruit tout seul en une minute.

**2. Les fichiers directement** (n'importe quel éditeur de texte) :

| Pour changer… | Ouvrir |
|---|---|
| Les prix, le contenu des séjours | `data/sejours.json` (mettre `"prix_confirme": true` quand le prix est validé, sinon le site affiche « tarif indicatif ») |
| Les dates où la maison est complète | `data/disponibilites.json` |
| Téléphone, WhatsApp, e-mail, moyens de paiement | `data/site.json` |
| Les notes Google / Booking / Tripadvisor et les extraits d'avis | `data/avis.json` |
| Un texte de page | `content/fr/<page>.md` (et `content/en/`, `content/de/`) |
| Une photo | déposer le fichier dans `static/images/` puis écrire `{{img: nom.jpg | légende}}` dans la page |

Dans les textes, `{{photo: légende}}` réserve un emplacement « photo à venir ». Remplacer par `{{img: fichier.jpg | légende}}` quand la photo existe.

## Photos d'illustration (maquette)

Pour visualiser le rendu avant les vraies photos, `data/maquette.json` associe des photos trouvées sur le web (dossier `static/images/mock-*.jpg`) aux emplacements « photo à venir ». Elles s'affichent avec la mention « photo d'illustration, à remplacer ». Elles ne doivent pas être publiées : mettre `"actif": false` avant la mise en ligne, ou supprimer les fichiers `mock-*`. Les sources sont listées dans le même fichier.

## Construire le site

```bash
python3 build.py
```

Le site est généré dans `public/`. Pour le voir en local :

```bash
python3 -m http.server 8765 --directory public
```

puis ouvrir http://127.0.0.1:8765/fr/.

Les images : pour chaque `nom.jpg` dans `static/images/`, ajouter si possible `nom.webp` et `nom-600.webp` (version légère pour les téléphones). Le script `tools/images.py` les fabrique.

## Hébergement

Prévu pour Netlify (gratuit) : `netlify.toml` contient la commande de construction, les redirections des anciennes adresses WordPress et la mise en cache des images. Le formulaire de réservation utilise Netlify Forms (attribut `data-netlify`). Sur un autre hébergeur, remplacer `form_action` dans `data/site.json` par l'adresse d'un service de formulaire (Formspree par exemple).

Pour l'administration à `/admin/`, activer Netlify Identity et Git Gateway dans les réglages du site Netlify, puis inviter Rachid par e-mail.

## À vérifier avant la mise en ligne

- Les prix des trois séjours et de la nuit seule (placeholders dans `data/sejours.json`).
- Les coordonnées GPS dans `data/site.json` (position actuelle prise sur OpenStreetMap, à confirmer par Rachid) et le lien de la fiche Google Business.
- Les temps de trajet et distances de la page Accès (Marrakech, Essaouira sont des estimations).
- Les notes Booking et Tripadvisor dans `data/avis.json`, et des extraits de ces deux plateformes.
- Les textes de la section « Les hôtes » et de la page « La vallée et l'eau » : écrits d'après les notes, à relire par Rachid. Vérifier en particulier la langue parlée à la maison (tachelhit) et les dates de la sécheresse.
- Les emplacements `{{photo: …}}` à remplacer par les photos de la semaine.
- Les moyens de paiement (virement, carte) dans `data/site.json`.
