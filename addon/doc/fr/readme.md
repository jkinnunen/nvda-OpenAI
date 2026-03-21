# AI Hub

Si vous souhaitez une experience bureau dediee avec des workflows supplementaires, consultez [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (application autonome avec une extension NVDA minimale). AI Hub reste une option complete integree a NVDA.

**AI Hub** est une extension NVDA qui connecte votre lecteur d'ecran a plusieurs API de modeles de langage (LLM). Vous pouvez l'utiliser pour rediger, resumer, traduire, decrire des images (captures et fichiers), poser des questions vocales, transcrire de l'audio et utiliser des outils optionnels (TTS, OCR, etc.) sans quitter NVDA.

Le **nom du paquet** dans NVDA reste `openai` (pour la compatibilite avec les installations existantes). Le **nom affiche** dans les menus et parametres est **AI Hub**.

## Apercu des fonctionnalites

- **Chat** dans une fenetre principale dediee avec historique, prompt systeme et selection modele/compte.
- **Images et documents** en pieces jointes depuis des fichiers; **URL** de fichiers distants avec verification du type selon le **fournisseur selectionne**.
- **Collage intelligent** dans le champ de prompt : collage de fichiers depuis le presse-papiers, chemins depuis du texte, ou URL unique (egalement via le menu contextuel du prompt). `Ctrl+V` applique la meme logique quand le prompt a le focus.
- **Historique des conversations** avec enregistrement, renommage, suppression et reouverture.
- **Poser une question** depuis n'importe ou (aucun raccourci par defaut) : assignez un geste dans **Gestes de commandes -> AI Hub** pour enregistrer, envoyer et ecouter/lire la reponse.
- **Description globale** : capture d'ecran (`NVDA+E`) ou zone de l'objet navigateur (`NVDA+O`) envoyee dans une session de chat.
- **Sous-menu Outils** (NVDA -> AI Hub) : utilitaires specifiques au fournisseur, comme TTS, OCR, speech-to-text, audio Lyria et gestion de modeles Ollama.
- Les options **raisonnement / recherche web** n'apparaissent que si le **modele courant** les prend en charge (selon le fournisseur).

Cette extension n'integre **pas** son propre verificateur de mises a jour. Les **mises a jour** sont gerees via le **Store officiel des extensions NVDA** si vous l'installez depuis celui-ci. Si vous installez manuellement depuis la [page des releases](https://github.com/aaclause/nvda-OpenAI/releases), installez les nouvelles versions `.nvda-addon` de la meme facon.

## Fournisseurs pris en charge

Configurez **un ou plusieurs fournisseurs** dans NVDA, **Preferences -> Parametres -> AI Hub**. Chaque fournisseur peut contenir **plusieurs comptes nommes** (cles API, et, selon le cas, organisation et URL de base).

| Fournisseur | Role |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT et modeles associes ; boites de dialogue officielles de transcription et TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek (compatible OpenAI) |
| **Custom OpenAI** | Toute API HTTP compatible OpenAI (URL de base personnalisee + cle) |
| **Ollama** | Modeles locaux via endpoint compatible OpenAI ; outil de gestion des modeles |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral ; outils Voxtral TTS, OCR et speech-to-text |
| [OpenRouter](https://openrouter.ai/) | Acces a de nombreux modeles tiers avec une seule cle |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini ; outil Lyria 3 Pro |

L'extension peut recuperer des cles API depuis des **variables d'environnement** si elles sont definies (par exemple `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY`, etc.). L'interface des parametres reste l'endroit principal pour gerer les comptes.

### Backends de transcription (speech-to-text)

Pour la **transcription micro / fichier** dans le flux principal (hors outil OpenAI dedie), vous pouvez choisir entre **whisper_cpp** (local), **openai** (API Whisper) et **mistral**, dans la section **Audio** des parametres AI Hub.

## Installation

1. Ouvrez la [page des releases de l'extension](https://github.com/aaclause/nvda-OpenAI/releases).
2. Telechargez le dernier paquet `.nvda-addon`.
3. Installez-le depuis **Outils -> Gestion des extensions** dans NVDA (ou ouvrez le fichier depuis l'Explorateur et confirmez l'installation).

## Configuration initiale

1. Ouvrez **NVDA -> Preferences -> Parametres**.
2. Selectionnez la categorie **AI Hub**.
3. Dans **Cles API**, utilisez les boutons de chaque fournisseur (ex. **Cles API OpenAI...**) pour ajouter au moins un compte : nom d'affichage, cle API, et champs optionnels (organisation, URL de base) selon le fournisseur.
4. Ajustez si besoin les options **Audio**, **Retour chat**, **Avance** / temperature, et **Sauvegarde automatique de la conversation** (activee par defaut).

Tant qu'aucun compte fournisseur n'est pret, l'ouverture de la fenetre principale vous proposera d'ajouter des cles dans les parametres AI Hub.

## Mise a niveau depuis les anciennes versions "Open AI"

Si vous utilisiez une ancienne version de cette extension :

- Les **parametres** sont migres depuis l'ancienne section de config **`OpenAI`** vers **`AIHub`**. Vous ne devriez pas perdre vos preferences.
- Les **donnees** (conversations, stockage de cles, pieces jointes) sont migrees du dossier **`openai`** vers **`aihub`** dans le repertoire de configuration utilisateur de NVDA.

Vous n'avez normalement rien a deplacer manuellement, sauf configuration speciale.

## Menu NVDA : AI Hub

Dans le menu NVDA, vous trouverez **AI Hub** (avec la version installee dans le libelle). Les entrees incluent :

- **Documentation** — ouvre le guide utilisateur dans le navigateur (`doc\en\readme.html`). Les paquets publies devraient inclure ce fichier ; il n'est **pas** modifie a la main : il est genere a partir de `readme.md` via l'etape de conversion markdown vers html du build.
- **Fenetre principale...** — ouvre la fenetre de chat (`NVDA+G` par defaut).
- **Historique des conversations...** — gere les conversations enregistrees.
- **Outils** — sous-menu regroupant les utilitaires **OpenAI**, **Mistral**, **Google** et **Ollama** (voir ci-dessous).
- **Cles API** / **Utilisation API** / **Depot GitHub** / **BasiliskLLM** — raccourcis rapides.

## Fenetre principale

Ouvrez-la avec **`NVDA+G`** ou via **Fenetre principale...** dans le menu AI Hub.

### Ce que vous pouvez faire

- Discuter avec le modele selectionne ; consulter les **Messages** avec navigation clavier et menus contextuels (ex. **j** / **k** pour passer au message precedent/suivant quand le focus est dans la zone de messages).
- Joindre des **images ou documents locaux** et ajouter des **URL de fichiers** quand le fournisseur les prend en charge.
- Utiliser **Coller (fichier ou texte)** depuis le menu contextuel du prompt, ou **`Ctrl+V`** dans le prompt : l'extension peut joindre des fichiers, inserer des chemins texte, ou traiter une URL unique comme piece jointe selon le contexte.
- Enregistrer des extraits **audio**, joindre des fichiers audio, et utiliser la **TTS** pour le texte du prompt si le modele le permet.
- **`Echap`** ferme la fenetre principale (si aucune boite modale bloquante n'est ouverte).
- **`Ctrl+R`** active/desactive l'enregistrement micro (selon disponibilite).
- **`F2`** renomme la conversation enregistree courante (une fois creee en stockage).
- **`Ctrl+N`** ouvre une **nouvelle** fenetre principale (session).

### Options dependantes du modele

Certaines options n'apparaissent ou ne s'appliquent que pour certains modeles :

- **Raisonnement** ("thinking") pour les modeles qui l'exposent ; le raisonnement stream peut rester separe de la reponse visible si l'API distingue les deux.
- **Effort de raisonnement** et options associees quand le fournisseur prend en charge des niveaux.
- **Recherche web** uniquement pour les modeles qui l'annoncent.

La disponibilite exacte peut evoluer selon les API ; l'interface reflete le **modele actuellement selectionne**.

### Prompt systeme

Le prompt systeme pilote le comportement du modele. Un prompt par defaut adapte a l'accessibilite est fourni ; vous pouvez l'editer, le reinitialiser depuis le menu contextuel, et optionnellement memoriser le dernier prompt utilise (configurable dans les parametres). Le prompt systeme consomme des tokens comme toute autre entree.

## Historique des conversations

Utilisez **Historique des conversations...** depuis le menu AI Hub, ou assignez un geste dans **Gestes de commandes -> AI Hub**.

Vous pouvez lister, ouvrir, renommer, supprimer et creer des conversations. Depuis la fenetre principale, **F2** et **Ctrl+N** aident a gerer la session en cours.

### Sauvegarde automatique

Si **Sauvegarde automatique de la conversation** est activee (defaut), l'extension enregistre (ou met a jour) la conversation stockee **apres chaque reponse assistant terminee**, et peut persister l'etat a la fermeture de la fenetre s'il y a du contenu a sauver. Vous pouvez aussi sauvegarder depuis le menu contextuel du champ **Messages**. Si la sauvegarde auto est desactivee, utilisez la sauvegarde manuelle.

## Poser une question (voix)

Cette commande n'a **pas de raccourci par defaut**. Assignez-en un dans **Gestes de commandes -> AI Hub**.

- Premier appui : demarrer l'enregistrement.
- Deuxieme appui pendant l'enregistrement : arreter et envoyer.
- Si la reponse est lue en audio, appuyez encore pour arreter la lecture.

**Modes :**

- **Audio direct** — si le modele selectionne prend en charge l'entree audio, votre enregistrement peut etre envoye directement sans etape de transcription separee.
- **Transcrire puis discuter** — sinon, le backend de transcription configure traite l'enregistrement, puis le texte est envoye au modele de chat.

Si la fenetre principale est active, son **modele courant** est utilise ; sinon l'extension choisit un modele adapte parmi les fournisseurs configures.

## Sous-menu Outils

L'entree **Outils** du menu AI Hub ouvre des boites de dialogue groupees par fournisseur (chacune peut necessiter un compte API correspondant) :

| Zone du menu | Outil |
|-----------|------|
| Mistral | **Voxtral TTS...**, **OCR...**, **Speech to Text...** |
| Google | **Lyria 3 Pro...** |
| OpenAI | **TTS...**, **Transcription / Traduction...** |
| Ollama | **Gestionnaire de modeles...** |

Si aucun compte n'est configure pour le fournisseur de l'outil, l'extension vous demandera d'en ajouter un dans les parametres AI Hub.

## Commandes globales

Tous les gestes par defaut peuvent etre modifies dans **NVDA -> Preferences -> Gestes de commandes -> AI Hub**.

| Geste | Action |
|---------|--------|
| `NVDA+G` | Afficher la fenetre principale AI Hub |
| `NVDA+E` | Capturer l'ecran et decrire (ajoute l'image a une session) |
| `NVDA+O` | Decrire la zone de l'objet navigateur courant |
| *(pas de geste par defaut)* | Historique des conversations. A assigner dans Gestes de commandes -> AI Hub. |
| *(pas de geste par defaut)* | Poser une question (enregistrer / envoyer / arreter l'audio). A assigner dans Gestes de commandes -> AI Hub. |
| *(pas de geste par defaut)* | Activer/desactiver l'enregistrement micro et la transcription. A assigner dans Gestes de commandes -> AI Hub. |

## Emplacement des donnees

Les fichiers de travail, l'index des conversations sauvegardees, `accounts.json` et les pieces jointes sont stockes dans le dossier **`aihub`** de la configuration utilisateur NVDA (apres migration depuis `openai`). Les fichiers temporaires utilisent un sous-dossier `tmp` et sont nettoyes quand c'est pertinent (ex. fermeture de boite de dialogue ou terminaison de l'extension).

## Dependances requises (recuperees automatiquement au build)

Les builds utilisent `scons` pour peupler les bibliotheques runtime dans :

`addon/globalPlugins/AIHub/libs/`

Si une bibliotheque requise est absente, `scons` telecharge des wheels epinglees et extrait uniquement ce qui est necessaire dans ce dossier. Dependances epinglees actuelles :

- **[markdown2](https://pypi.org/project/markdown2/)** `2.5.4` — extrait comme `libs/markdown2.py` pour le rendu Markdown du chat.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` pour :
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

Le dossier `libs` est volontairement ignore par git ; les contributeurs n'ont pas a versionner ces artefacts.

## Depannage (court)

- **"Aucun compte configure"** — Ajoutez une cle API pour le fournisseur selectionne dans les parametres **AI Hub**.
- **Le fournisseur refuse une piece jointe** — Verifiez le type et la taille du fichier ; essayez un autre modele ou fournisseur compatible.

Pour signaler un probleme ou contribuer, utilisez le lien **GitHub repository** depuis le menu AI Hub.
