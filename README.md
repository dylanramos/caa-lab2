# CAA Lab 2

## Utilisation de l'IA

Des outils d'IA générative ont été utilisés pour trouver et corriger les erreurs cryptographiques dans le code fourni. Cependant, le rapport a lui été entièrement rédigé par mes soins.

## Génération des nombres aléatoires

- Ligne **73** : `priv = random.randrange(1, N)`
- Ligne **80** : `k = random.randrange(0, N)`

### Explication technique

La génération des nombres aléatoires n'est pas cryptographiquement sûre. Ainsi, un attaquant pourrait récupérer la clé privée de la plateforme en prédisant `k` ou si `k` est réutilisé.

D'autre part, à la ligne 80, la plage de nombres aléatoires est fausse car `k` risque d'être égal à 0, ce qui ne correspond pas au standard et pourrait faire planter le programme à la ligne 82 (`r = R[0] % N`).

### Explication simplifiée

Un hackeur pourrait deviner les nombres secrets utilisés pour sécuriser les messages et ainsi se faire passer pour :
- Un patient légitime et modifier ses symptômes, ce qui peut entraîner des prescriptions inappropriées et potentiellement mettre en danger la santé du patient.
- Un médecin légitime et prescrire des médicaments non autorisés ou dangereux, ce qui pourrait mettre en danger la santé des patients.

## Cryptographie "maison"

- Lignes **17-104** : fonctions `inv_mod()`, `is_on_curve()`, `point_add()`, `scalar_mult()`, `generate_keypair()`, `sign_message()`, `verify_signature()`

### Explication technique

Implémenter sa propre cryptographie est difficile et sujet à des erreurs d'arithmétique, de validation et de cas limites. Un attaquant pourrait exploiter ces erreurs pour casser la sécurité de la plateforme. Par exemple, le temps que prend la fonction `scalar_mult()` à s'exécuter dépend de `k`, ce qui pourrait permettre à un attaquant de récupérer la clé privée en mesurant le temps d'exécution (attaque par canal auxiliaire).

### Explication simplifiée

Il existe des algorithmes de sécurité beaucoup plus sûrs et fiables qui ont été largement éprouvés et testés par des mathématiciens et des experts en sécurité. En créant nos propres algorithmes, nous risquons de faire des erreurs que des hackeurs pourraient exploiter pour voler des informations sensibles ou se faire passer pour des utilisateurs légitimes.

## Stockage de la clé privée

- Lignes **145-164** : fonction `load_or_generate_keys()`

### Explication technique

La clé privée est stockée en clair sur le disque. Ainsi, si le système est compromis, un attaquant pourrait voler la clé privée et donc signer n'importe quel message.

### Explication simplifiée

Nous avons une clé secrète qui permet à l'application de garantir que les messages proviennent bien des patients et des médecins légitimes. Or, cette clé est stockée sur le serveur sans aucune protection. Si un hackeur ou une personne malveillante parviennent à accéder au serveur (physiquement ou via une faille de sécurité), ils pourraient voler cette clé secrète et se faire passer pour des utilisateurs légitimes, ce qui pourrait nuire à la réputation des médecins et mettre en danger la santé des patients.

## Stockage des enregistrements

- Lignes **135-143** : fonction `save_record_to_db()`

### Explication technique

La signature ne couvre que les enregistrements (nom du patient, numéro AVS, etc.), le timestamp n'est pas inclus dans la signature. Ainsi, un attaquant avec un accès à la base de données pourrait modifier le timestamp d'un enregistrement sans invalider la signature.

### Explication simplifiée

L'application protège les informations enregistrées par les utilisateurs mais elle ne protège pas la date et l'heure auxquelles ces informations ont été enregistrées. Un hackeur ou une personne malveillante pourrait modifier cette date et heure pour faire croire que les informations ont été enregistrées à un autre moment, ce qui pourrait causer des erreurs dans le suivi médical des patients.

## Utilisation d'une courbe elliptique peu courante

- Lignes **9-14** : paramètres de la courbe elliptique

### Explication technique

La courbe elliptique `Secp256k1` est sécurisée et bien connue pour être utilisée dans Bitcoin mais elle a une structure mathématique particulière (courbe de Koblitz) qui est plutôt destinée à des applications en lien avec la blockchain. Il serait préférable d'utiliser une courbe elliptique plus commune destinée à des applications générales, comme `Secp256r1`, qui est plus largement utilisée dans l'industrie.

### Explication simplifiée

L'application utilise une structure mathématique particulière pour sécuriser les messages. Bien que sécurisée et recommandée par le NIST, cette structure est peu courante pour ce type d'application car elle est principalement utilisée pour des monnaies numériques comme le Bitcoin. Il serait préférable d'utiliser une structure plus courante et largement adoptée dans l'industrie pour garantir une meilleure compatibilité et sécurité.

## Design de cryptographique de l'application

### Explication technique

Il n'y a qu'une seule paire de clés (publique/privée) pour toute la plateforme, cela signifie qu'il n'y a pas de non-répudiation possible. De plus, si un attaquant parvient à compromettre la clé privée, il pourrait signer n'importe quel message pour n'importe quel utilisateur.

### Explication simplifiée

L'application n'utilise qu'une seule clé secrète pour tous les utilisateurs. Cette clé garantit que les messages proviennent bien de la plateforme mais elle ne permet pas de déterminer qui a créé quoi. C'est un problème car :

- Un patient pourrait nier avoir enregistré certains symptômes.
- Un médecin pourrait nier avoir prescrit certains médicaments.

De plus, l'utilisation d'une seule clé secrète pour tous les utilisateurs pose un risque important. Si un hackeur ou une personne malveillante parvient à voler cette clé secrète, ils pourraient se faire passer pour n'importe quel utilisateur légitime de l'application, ce qui pourrait entraîner des erreurs médicales graves et nuire à la réputation des médecins.

### Solution

Chaque utilisateur devrait avoir sa propre paire de clés publique/privée. Ainsi, même si la clé privée d'un utilisateur est compromise, les autres utilisateurs restent protégés. L'application servirait donc de tiers de confiance pour vérifier que les clés publiques des utilisateurs correspondent bien à leur identité et la non-répudiation serait assurée.

Je n'ai pas implémenté cette solution car il faudrait repenser et modifier l'architecture de l'application.

## Corrections effectuées

Le fichier `dep_patch.py` contient les corrections apportées au code initial.

- J'utilise la librairie `cryptography` au lieu d'implémenter une cryptographie "maison".
- Je stocke la clé privée sur le disque de manière sécurisée en la chiffrant avec un mot de passe.
- J'inclus le timestamp dans les données signées pour éviter toute modification des enregistrements.
- J'utilise la courbe elliptique `SECP256R1` au lieu de `SECP256K1`.