# Maison d'hôtes Tifrit — proposition de nouveau site

Version 2 (après les notes de positionnement) : site multi-pages en trois langues, généré par `build.py`. Voir `README.md` pour le mode d'emploi.

> La section 2 ci-dessous décrit la première maquette (une page). La version 2 la remplace : voir la section 6.

## 1. Constat sur le site actuel (tifritecolodge.com)

- **Certificat SSL expiré** : les navigateurs affichent un avertissement de sécurité avant même d'arriver sur le site. À corriger en priorité chez l'hébergeur (Let's Encrypt).
- **WordPress + Elementor** (WordPress 7.1, Elementor 4.3, thème « hôtel » générique par Agadir Concept) : lourd, à maintenir (mises à jour, plugins), et le rendu est celui d'un template d'hôtel standard, pas d'un écolodge.
- **Anglais par défaut**, le français est à `/fr/accueil/` ; la page `/fr/chambres` renvoie une 404.
- **Textes génériques** (« The Luxury Experience You'll Remember ») en contradiction avec l'identité voulue : simplicité, terroir, écologie.
- **Blog** avec trois articles vides « Article 1 / 2 / 3 ».
- **Contact** : un numéro de fax factice (0123 456 789), deux numéros de téléphone différents selon les pages (0661 654 231 et 0661 389 893).
- **Chambres** : une seule « room details » (3 pers., 38 m², 35 $), pas de vue d'ensemble des chambres ni des tarifs.
- **Photos** : photos de téléphone en format portrait, chambres sans mise en scène, une photo de plat issue d'une banque d'images.
- **Formulaire de réservation** avec champ « Company Name » obligatoire et captcha texte.
- Rien sur l'écologie, les matériaux de construction, les producteurs.

## 2. Ce que propose la maquette

### Positionnement

« Une maison de terre, de bois et de paille, nichée dans la palmeraie, au cœur de la Vallée du Paradis. »
Trois promesses, répétées partout : **au milieu de la nature**, **parfait pour les randonneurs**, **nourrie par le terroir**.

### Structure (une seule page longue + ancres, extensible en pages)

1. **Accueil** : grande photo, phrase d'accroche, deux boutons (Réserver / Voir les randonnées).
2. **Manifeste** : une citation et les trois promesses.
3. **La maison** : photo de la maison dans la palmeraie, texte sur la construction, trois cartes matériaux (terre crue, bois, paille).
4. **Chambres** : trois types avec photo, capacité, équipements, prix « à partir de ».
5. **La table** : mosaïque de photos et six produits du terroir (miel de thym, argan, amlou, pain, légumes, tajines).
6. **Randonnées & excursions** : piscines naturelles, oasis berbère, ruches d'Inzerki, dunes de Tamri (repris du site actuel, reformulé).
7. **Engagements** : six engagements concrets numérotés (matériaux, eau de source, solaire, circuits courts, zéro plastique, emploi local).
8. **Témoignages** : trois vrais avis Google du site actuel (Germain, Laura, Julian).
9. **Accès** : distances, carte OpenStreetMap, infos pratiques.
10. **Réserver** : WhatsApp en premier, téléphone, e-mail, réseaux, formulaire court (dates, voyageurs, chambre, nom, e-mail).

### Direction artistique

- **Couleurs** : sable (`#f4ecdd`), terre cuite (`#9a5537`), ocre (`#c98a4b`), paille (`#e3c27f`), vert olive foncé (`#3f4d27`). Palette tirée des matériaux (terre, paille, arganiers).
- **Typographies** : Fraunces (titres, serif chaleureux) + Manrope (texte). Google Fonts, gratuites.
- **Ton** : phrases courtes, concrètes, à la première personne du pluriel. Pas de « luxe », pas de superlatifs.
- **Logo** : l'arche dorée actuelle est reprise en pied de page. Elle peut être conservée ; une version simplifiée (arche seule, en terre cuite) irait mieux avec la nouvelle identité.

### Technique

- HTML + CSS + 15 lignes de JavaScript, aucune dépendance, aucun CMS. Hébergeable gratuitement (Netlify, Cloudflare Pages, GitHub Pages) ou sur l'hébergeur actuel.
- Poids total de la page avec les photos : environ 6 Mo, à diviser par deux en passant les images en WebP quand les nouvelles photos arriveront.
- Responsive (ordinateur, tablette, téléphone) ; menu burger sur mobile.
- Le formulaire envoie un e-mail via `mailto:`. Pour un vrai formulaire, brancher Formspree, Netlify Forms, ou un lien direct vers un moteur de réservation.

## 3. Ce qui reste à décider ou vérifier (contenu)

- [ ] Nom de domaine : garder **tifritecolodge.com** (et réparer le SSL) ? L'ancien maisondhotestifrit.com est expiré.
- [ ] **Tarifs** des chambres : la maquette affiche « à partir de 35 € » (valeur du site actuel) et « tarif sur demande » pour la suite. À confirmer.
- [ ] **Types de chambres** réels (noms, capacités, surfaces, lesquelles ont une cheminée et une terrasse privée).
- [ ] **Numéro de téléphone** unique à afficher (654 231 ou 389 893 ?) et numéro WhatsApp.
- [ ] **E-mail** : contact@tifritecolodge.com ?
- [ ] **Engagements écologiques** : la maquette propose six engagements plausibles (solaire, récupération d'eau, compost…). Ne garder que ce qui est vrai ou prévu, et le dire honnêtement (« en cours »).
- [ ] **Construction terre / bois / paille** : quelle partie de la maison est concernée (extension, nouvelles chambres, rénovation) ? Dates du chantier ? Un chantier participatif serait un très bon sujet de page.
- [ ] **Producteurs** : noms des coopératives d'argan et des apiculteurs à citer.
- [ ] Langues : français d'abord, puis anglais (et allemand : une partie des avis Google est en allemand).

## 4. Plan de prise de vue pour les nouvelles photos

Format paysage (horizontal) pour la plupart, lumière du matin ou de fin d'après-midi, téléphone récent suffit si tenu droit. Liste par ordre d'importance :

1. **La maison dans la palmeraie**, de loin, au lever ou au coucher du soleil (photo d'accueil).
2. **La piscine** avec les palmiers et la montagne derrière, sans les parasols fermés, transats alignés.
3. **Un mur de terre** en gros plan (texture), et un mur en cours de construction (paille, terre, bois) si le chantier existe.
4. **Chaque type de chambre** : lit fait, rideaux ouverts, lumière naturelle, une photo depuis la porte et une depuis le lit vers la terrasse. Retirer les objets du quotidien (prises multiples, bouteilles).
5. **La terrasse privée** avec la vue montagne, une tasse de thé posée.
6. **Le petit-déjeuner** servi : pain, amlou, miel, huile d'argan, fruits, thé, vu de dessus.
7. **Un tajine** sortant de la cuisine, et le salon avec la cheminée allumée.
8. **Les mains** : quelqu'un qui pétrit le pain, verse le thé, récolte au jardin.
9. **Les piscines naturelles** et le sentier qui y mène, avec une personne de dos pour l'échelle.
10. **Rachid** (l'hôte), portrait simple devant la maison ou en randonnée.
11. **Les producteurs** : la coopérative d'argan, les ruches.
12. **Détails** : enduit à la chaux, bois des plafonds, lanterne, tapis, porte.

Les photos d'emprunt (Wikimedia Commons, voir `CREDITS.md`) sont là pour montrer l'intention ; elles doivent être remplacées avant la mise en ligne ou créditées en pied de page.

## 5. Étapes suivantes

1. Valider la structure et le ton de la maquette, corriger les faits (tarifs, chambres, contacts).
2. Faire les photos selon le plan ci-dessus.
3. Remplacer les images, passer en WebP, ajouter la version anglaise.
4. Brancher un vrai formulaire ou un moteur de réservation, puis mettre en ligne sur le domaine avec un certificat SSL valide.
5. Rediriger les anciennes URL du WordPress (`/about/`, `/rooms/...`, `/fr/accueil/`) vers les ancres de la nouvelle page pour ne pas perdre le référencement.

## 6. Version 2 : ce qui a changé après les notes

- **Produit** : le site vend un séjour de 3 à 5 jours avec Rachid, pas une chambre. Page « Les séjours » avec trois formules (phare, famille, marcheurs), programme jour par jour, inclus, « ce n'est pas fait pour », prix tout compris. Les chambres passent en fin de page « La maison ».
- **Nom unique** : « Maison d'hôtes Tifrit » partout. Pas d'« éco » dans les titres ; les faits (source, solaire, plastique, producteurs) sont sur la page « La vallée et l'eau ».
- **Pages** : Accueil, La maison, Les séjours, Rachid, La vallée et l'eau, Accès, Avis, Journal (3 articles), Réserver.
- **Trois langues** avec sélecteur, URLs par langue (`/fr/`, `/en/`, `/de/`), balises hreflang, sitemap.
- **Photos** : uniquement les photos actuelles de la maison, plus des emplacements « photo à venir » nommés pour celles de la semaine (Rachid, eau, chambres, drone, expérience). Plus aucune image de banque. WebP + version 600 px pour la 4G.
- **Conversion** : WhatsApp en un clic avec message pré-rempli, formulaire court, moyens de paiement affichés, calendrier de disponibilité manuel.
- **Référencement** : titres et descriptions par page avec les mots-clés cibles, données structurées LodgingBusiness, champ pour la fiche Google Business, redirections des anciennes URL WordPress.
- **Technique** : statique, un script Python sans dépendance, contenus en Markdown et JSON, interface d'édition Decap CMS à `/admin/` pour Rachid. Pas de webfont, 15 lignes de JavaScript.
- **Aucune mention de la chasse**, ni texte ni image.

## 7. Direction artistique v2 (après le retour « pas assez moderne »)

- **Typographie éditoriale** : Instrument Serif pour les titres, très grands (jusqu'à 7 rem sur l'accueil), DM Sans pour le texte. Deux fichiers de police, chargés depuis Google Fonts.
- **Couleurs** : fond blanc cassé chaud, encre presque noire, un seul accent terre cuite, et une section sombre vert forêt pour la formule phare. Fini le beige « sable » partout.
- **Accueil** : photo plein écran avec léger zoom lent, titre en bas à gauche, phrase et bouton à droite, bandeau de faits clés en bas (altitude, distance, six chambres, source).
- **Navigation** : fixe, transparente sur la photo puis fond flouté au défilement. Sélecteur de langue en pilule.
- **Blocs** : plus d'ombres ni de cartes en boîtes. Lignes fines, grands arrondis (22 px) pour les photos et les formules, numéros 01 02 03 en serif.
- **Galerie** : première photo en grand format, les autres en grille ; sur mobile, défilement horizontal avec accroche.
- **Mobile** : barre « Réserver sur WhatsApp » fixée en bas de l'écran sur toutes les pages.
- **Mouvement** : apparition en fondu au défilement, désactivée si l'utilisateur préfère réduire les animations.
