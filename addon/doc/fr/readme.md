Si vous souhaitez une expérience de bureau dédiée avec des flux de travail supplémentaires, consultez [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (application autonome avec un module complémentaire NVDA minimal). AI-Hub reste une solution complète intégrée à NVDA.

# AI-Hub

**AI-Hub** est un module complémentaire NVDA qui connecte votre lecteur d’écran à plusieurs API de grands modèles de langage (LLM). Utilisez-le pour écrire, résumer, obtenir de l’aide à la traduction, analyser des images (photos et captures d’écran), poser des questions à la voix, transcrire, et ouvrir des boîtes de dialogue d’outils optionnelles (TTS, OCR, etc.) — sans quitter NVDA.

Le **nom de paquet** du module dans NVDA est toujours `openai` (pour la compatibilité avec les installations existantes). Le **nom d’affichage** visible dans les menus et paramètres est **AI-Hub**.

## Fonctionnalités en un coup d’œil

- **Chat** dans une fenêtre principale dédiée, avec historique, prompt système et sélection du modèle/compte.
- **Images et documents** en pièces jointes depuis des fichiers ; **URL** vers des fichiers distants avec vérifications de type alignées sur le **fournisseur sélectionné**.
- **Collage intelligent** dans le champ de prompt : collez des fichiers depuis le presse-papiers, des chemins depuis du texte, ou une URL unique (également disponible dans le menu contextuel du prompt). `Ctrl+V` applique la même logique lorsque le prompt a le focus.
- **Enregistrement des conversations et historique** avec renommage, suppression et réouverture.
- **Poser une question** depuis n’importe où (aucune touche par défaut) : assignez un geste dans **Gestes de commandes → AI-Hub** pour enregistrer, envoyer, puis écouter ou lire la réponse.
- **Description globale** : capture d’écran (`NVDA+E`) ou région de l’objet navigateur (`NVDA+O`) envoyée dans une session de chat.
- **Sous-menu Outils** (sous NVDA → AI-Hub) : utilitaires spécifiques aux fournisseurs comme la TTS, l’OCR, la parole-vers-texte, l’audio Lyria et la gestion des modèles Ollama.
- Les options **raisonnement / recherche web** n’apparaissent que lorsque le **modèle courant** les prend en charge (cela varie selon le fournisseur).

Ce module ne comprend **pas** son propre vérificateur de mises à jour. Les **mises à jour** sont gérées via le **Store officiel des modules NVDA** lorsque vous l’installez depuis celui-ci. Si vous l’installez manuellement depuis la [page des publications](https://github.com/aaclause/nvda-OpenAI/releases), installez les nouvelles versions `.nvda-addon` de la même manière.

## Fournisseurs pris en charge

Configurez **un ou plusieurs fournisseurs** dans NVDA, **Préférences → Paramètres → AI-Hub**. Chaque fournisseur peut contenir **plusieurs comptes nommés** (clés API, organisation facultative ou URL de base, selon le cas).

| Fournisseur | Rôle |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT et modèles associés ; boîtes de dialogue officielles de transcription et TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek (compatible OpenAI) |
| **Custom OpenAI** | Toute API HTTP compatible OpenAI (URL de base personnalisée + clé) |
| **Ollama** | Modèles locaux via un point de terminaison compatible OpenAI ; outil de gestion des modèles |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral ; outils Voxtral TTS, OCR et parole-vers-texte |
| [OpenRouter](https://openrouter.ai/) | De nombreux modèles tiers derrière une seule clé |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini ; outil Lyria 3 Pro |

Le module peut récupérer des clés API via des **variables d’environnement** lorsqu’elles sont définies (par exemple `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY`, entre autres). L’interface des paramètres reste l’endroit principal pour gérer vos comptes.

### Moteurs de parole vers texte (transcription)

Pour la **transcription micro / fichier** dans le flux principal (et non via l’outil OpenAI de transcription séparé), vous pouvez choisir entre **whisper_cpp** (local), **openai** (API Whisper), et **mistral**, dans la section **Audio** des paramètres d’AI-Hub.

## Installation

1. Ouvrez la [page des publications du module](https://github.com/aaclause/nvda-OpenAI/releases).
2. Téléchargez le dernier paquet `.nvda-addon`.

## Configuration initiale

1. Ouvrez **NVDA → Préférences → Paramètres**.
2. Sélectionnez la catégorie **AI-Hub**.
3. Dans **API Accounts**, choisissez **Add account...**.
4. Dans la boîte de dialogue de compte, choisissez un fournisseur, saisissez un nom de compte et renseignez les champs requis (clé API pour la plupart des fournisseurs; URL de base pour **Custom OpenAI** et **Ollama**, Ollama utilisant par défaut http://127.0.0.1:11434/v1 si le champ est vide).
5. Enregistrez, puis ajoutez éventuellement d'autres comptes, modifiez les comptes existants ou supprimez ceux inutilisés de la liste.
6. Ajustez éventuellement **Audio**, **Chat feedback**, **Advanced** / température et **Auto-save conversation** (activé par défaut).

Tant qu’au moins un compte fournisseur n’est pas configuré, l’ouverture de la fenêtre principale vous invitera à ajouter des clés dans les paramètres d’AI-Hub.

## Mise à niveau depuis les anciennes versions « Open AI »

Si vous utilisiez une ancienne version de ce module :

- Les **paramètres** sont migrés depuis l’ancienne section de configuration **`OpenAI`** vers **`AIHub`**. Vous ne devriez pas perdre vos préférences.
- Les **fichiers de données** (conversations, magasin de clés, pièces jointes) sont migrés depuis le dossier **`openai`** de votre répertoire de configuration utilisateur NVDA vers **`aihub`**.

Vous n’avez pas besoin de déplacer les fichiers manuellement, sauf si vous utilisez une configuration personnalisée.

## Menu NVDA : AI-Hub

Dans le menu NVDA, vous trouverez **AI-Hub** (avec la version installée dans le libellé). Les entrées incluent :

- **Documentation** — ouvre le guide utilisateur dans votre navigateur (`doc\en\readme.html`).
- **Fenêtre principale…** — ouvre la fenêtre de chat (`NVDA+G` par défaut).
- **Historique des conversations…** — gère les conversations enregistrées.
- **Outils** — sous-menu qui regroupe les utilitaires **OpenAI**, **Mistral**, **Google** et **Ollama** (voir ci-dessous).
- **GitHub repository** / **BasiliskLLM** - liens rapides.

## Fenêtre principale

Ouvrez-la avec **`NVDA+G`** ou via **Fenêtre principale…** depuis le menu AI-Hub.

### Ce que vous pouvez faire

- Discuter avec le modèle sélectionné ; consulter **Messages** via la navigation clavier et les menus contextuels (par ex. **j** / **k** pour passer d’un message à l’autre lorsque le focus est dans la zone de messages — voir les indications à l’écran pour le champ actif).
- Joindre des **images ou documents locaux** et ajouter des **URL de fichiers** lorsque le fournisseur les prend en charge. Les types non pris en charge par le fournisseur actuel peuvent déclencher un avertissement avant l’envoi.
- **Coller (fichier ou texte)** depuis le menu contextuel du prompt, ou **`Ctrl+V`** dans le prompt : le module peut joindre des fichiers, insérer des chemins texte, ou traiter une URL unique comme pièce jointe lorsque cela s’applique.
- Enregistrer des extraits **audio**, joindre des fichiers audio, et utiliser la **TTS** pour le texte du prompt lorsque le modèle le permet.
- **`Échap`** ferme la fenêtre principale (lorsqu’aucune boîte modale bloquante n’est ouverte).
- **`Ctrl+R`** active/désactive l’enregistrement du microphone (si applicable).
- **`F2`** renomme la conversation enregistrée courante (une fois qu’elle existe dans le stockage).
- **`Ctrl+N`** ouvre une **nouvelle** instance de fenêtre principale (session).

### Options qui dépendent du modèle

Certains contrôles n’apparaissent ou ne s’appliquent qu’à certains modèles :

- **Raisonnement** (« thinking ») pour les modèles qui l’exposent ; le raisonnement diffusé peut être conservé séparément de la réponse visible lorsque l’API prend en charge cette distinction.
- **Effort de raisonnement** et contrôles associés lorsque le fournisseur prend en charge des niveaux.
- **Recherche web** uniquement pour les modèles qui annoncent la prise en charge de la recherche web.

La disponibilité exacte évolue au rythme des API des fournisseurs ; l’interface reflète le **modèle actuellement sélectionné**.

### Prompt système

Le prompt système oriente le comportement du modèle. Un prompt par défaut adapté à l’assistance en accessibilité est fourni ; vous pouvez l’éditer, le réinitialiser depuis le menu contextuel, et éventuellement conserver le dernier prompt utilisé (configurable dans les paramètres). Le prompt système consomme des jetons, comme n’importe quelle autre entrée.

## Historique des conversations

Utilisez **Historique des conversations…** depuis le menu AI-Hub, ou assignez un geste dans **Gestes de commandes → AI-Hub**.

Vous pouvez lister, ouvrir, renommer, supprimer et créer des conversations. Depuis la fenêtre principale, **F2** et **Ctrl+N** vous aident à gérer la session courante.

### Sauvegarde automatique

Si **Sauvegarde automatique de la conversation** est activée dans les paramètres (par défaut), le module enregistre (ou met à jour) la conversation stockée **après chaque réponse de l’assistant terminée**, et peut conserver l’état lorsque vous fermez la fenêtre s’il y a quelque chose à sauvegarder. Vous pouvez aussi enregistrer depuis le menu contextuel du champ **Messages**. Si la sauvegarde automatique est désactivée, utilisez l’enregistrement manuel quand vous souhaitez conserver la conversation.

## Poser une question (voix)

Cette commande n’a **aucune touche par défaut**. Assignez-en une dans **Gestes de commandes → AI-Hub**.

- Premier appui : démarrer l’enregistrement.
- Deuxième appui pendant l’enregistrement : arrêter et envoyer.
- Si la réponse est lue en audio, appuyez de nouveau pour arrêter la lecture.

**Modes :**

- **Audio direct** — si le modèle sélectionné prend en charge l’entrée audio, votre enregistrement peut être envoyé directement, sans étape de transcription séparée.
- **Transcrire puis discuter** — sinon, le moteur de transcription configuré traite l’enregistrement, puis le texte est envoyé au modèle de chat.

Si la fenêtre principale a le focus, son **modèle courant** est utilisé ; sinon, le module choisit un modèle approprié parmi les fournisseurs configurés.

## Sous-menu Outils

L’entrée **Outils** du menu AI-Hub ouvre des boîtes de dialogue groupées par fournisseur (chacune pouvant nécessiter le compte API correspondant) :

| Zone de menu | Outil |
|-----------|------|
| Mistral | **Voxtral TTS…**, **OCR…**, **Speech to Text…** |
| Google | **Lyria 3 Pro…** |
| OpenAI | **TTS…**, **Transcription / Traduction…** |
| Ollama | **Gestionnaire de modèles…** |

Si aucun compte n’est configuré pour le fournisseur d’un outil, le module vous indiquera d’en ajouter un dans les paramètres d’AI-Hub.

## Commandes globales

Toutes les touches par défaut peuvent être modifiées dans **NVDA → Préférences → Gestes de commandes → AI-Hub**.

| Geste | Action |
|---------|--------|
| `NVDA+G` | Afficher la fenêtre principale AI-Hub |
| `NVDA+E` | Capture d’écran et description (ajoute l’image à une session) |
| `NVDA+O` | Décrire la région de l’objet navigateur courant |
| *(aucun geste par défaut)* | Historique des conversations. Assignez-le dans Gestes de commandes → AI-Hub. |
| *(aucun geste par défaut)* | Poser une question (enregistrer / envoyer / arrêter l’audio). Assignez-le dans Gestes de commandes → AI-Hub. |
| *(aucun geste par défaut)* | Activer/désactiver l’enregistrement micro et la transcription. Assignez-le dans Gestes de commandes → AI-Hub. |

## Où les données sont stockées

Les fichiers de travail, l’index des conversations enregistrées, le fichier unifié `accounts.json` et les pièces jointes se trouvent dans le dossier **`aihub`** de votre configuration **utilisateur** NVDA (après migration depuis `openai`). Les fichiers temporaires utilisent un sous-dossier `tmp` et sont nettoyés lorsque c’est raisonnable (par ex. à l’arrêt du module ou à la fermeture de la fenêtre).

## Dépendances requises (récupérées automatiquement pendant le build)

Les builds utilisent `scons` pour remplir les bibliothèques d’exécution dans :

`addon/globalPlugins/AIHub/libs/`

Quand une bibliothèque requise est manquante, `scons` télécharge des wheels épinglées et extrait uniquement ce qui est nécessaire dans ce dossier. Les dépendances actuellement épinglées sont :

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — extrait vers `libs/` pour le rendu Markdown du chat.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1` pour :
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

Le dossier `libs` est volontairement ignoré par git ; les contributeurs n’ont pas besoin de versionner les artefacts embarqués.

## Dépannage (court)

- **« Aucun compte configuré »** — Ajoutez une clé API pour le fournisseur sélectionné dans les paramètres **AI-Hub**.
- **Le fournisseur refuse une pièce jointe** — Vérifiez le type et la taille du fichier ; essayez un autre modèle ou fournisseur qui prend en charge le média dont vous avez besoin.

Pour les signalements de problèmes et les contributions, utilisez le lien **Dépôt GitHub** depuis le menu AI-Hub.
