# Procédure de Démonstration des Capacités de SmartMemory

Ce document décrit une série de tests pratiques permettant de démontrer les capacités uniques (inédites) de SmartMemory, en mettant l'accent sur la traçabilité, le raisonnement hybride et la recherche sémantique avancée.

## Prérequis

- Serveur MCP SmartMemory actif.
- Un client MCP (Claude Desktop, Gemini, ou client CLI).
- Le backend Oxigraph activé pour des performances optimales.

---

## Test 1 : Recherche Sémantique et "Labels Cachés"

**Objectif** : Démontrer que SmartMemory peut identifier des entités même avec des alias ou des noms alternatifs (SKOS), et révéler des propriétés structurées.

1. **Action** : Ajouter une entité avec un alias SKOS.
   - *Outil* : `add_memory`
   - *Entrée* : `:Thales foaf:name "Thales" ; skos:altLabel "Thomson-CSF" ; a :Organization .`
2. **Action** : Rechercher via l'ancien nom.
   - *Outil* : `search_entity`
   - *Entrée* : `search_term="Thomson"`
3. **Résultat attendu** :
   - SmartMemory trouve "Thales" car il a indexé le `altLabel`.
   - Il affiche l'URI, le type (Organization) et les propriétés associées, en filtrant automatiquement les métadonnées techniques de provenance.

---

## Test 2 : Raisonnement avec Incertitude (Human-in-the-Loop)

**Objectif** : Démontrer la capacité du système à détecter des faits probables mais nécessitant une validation humaine.

1. **Action** : Créer une règle qui génère de l'incertitude.
   - *Fichier* : `src/rules/custom/security_check.rq`
   - *Contenu* :

     ```sparql
     # Description: Détecte les accès sensibles potentiels
     # Version: 1.0.0
     # Author: Daniel
     PREFIX : <http://semanticmemory.org/user#>
     PREFIX sem: <http://semanticmemory.org/vocab#>
     CONSTRUCT {
         ?user :hasAccessTo :SecretProject .
         ?user sem:uncertainPredicate :hasAccessTo .
     }
     WHERE {
         ?user :worksFor :Thales .
         ?user :role "SecurityManager" .
     }
     ```

2. **Action** : Ajouter un utilisateur correspondant.
   - *Outil* : `add_memory`
   - *Entrée* : `:Gilles :worksFor :Thales ; :role "SecurityManager" .`
3. **Action** : Vérifier les inférences en attente.
   - *Outil* : `get_pending_verifications`
4. **Résultat attendu** :
   - Gilles est proposé pour l'accès au `SecretProject`.
   - Le système ne l'ajoute pas directement au graphe de vérité mais attend une validation.

---

## Test 3 : Traçabilité Totale et Provenance

**Objectif** : Démontrer que chaque bit d'information est sourcé et versionné.

1. **Action** : Lister les règles pour voir l'auteur du test précédent.
   - *Outil* : `list_rules`
2. **Résultat attendu** :
   - La règle `security_check` apparaît avec `Author: Daniel` et `Version: 1.0.0`.
3. **Action** : Examiner la provenance d'un triple.
   - *Outil* : `inspect_provenance` (ou via une requête SPARQL directe sur le graphe de provenance).
4. **Résultat attendu** :
   - On voit exactement quel agent (ou utilisateur) a ajouté le fait, à quelle date, et avec quel niveau de confiance.

---

## Test 4 : Le "Droit à l'Oubli" Propre (Forget Memory)

**Objectif** : Démontrer que la suppression d'un fait nettoie également toutes les métadonnées de provenance associées (reification RDF).

1. **Action** : Supprimer un fait.
   - *Outil* : `forget_memory`
   - *Entrée* : `:Gilles :worksFor :Thales`
2. **Action** : Vérifier le compte de triples.
   - *Outil* : `get_triple_count`
3. **Résultat attendu** :
   - Le compteur diminue de manière atomique (O(1)).
   - Les nœuds de type `rdf:Statement` liés à ce fait ont disparu du graphe, évitant la pollution de données ("ghost triples").

---

## Test 5 : Performance Multi-Backend (Oxigraph)

**Objectif** : Démontrer la montée en charge.

1. **Action** : Configurer `SEMMEM_PERSISTENCE_BACKEND=oxigraph`.
2. **Action** : Charger une ontologie complexe ou des milliers de faits.
3. **Résultat attendu** :
   - Les requêtes `search_entity` et l'exécution des règles restent instantanées (< 100ms) grâce au stockage B-Tree natif d'Oxigraph, là où le format Turtle commencerait à ralentir.

---

## Conclusion

SmartMemory n'est pas qu'une base de données RDF ; c'est un **système de gestion de la connaissance active** qui combine :

- **Rigueur sémantique** (Ontologies, SPARQL).
- **Flexibilité LLM** (Extraction, Suggestion).
- **Gouvernance** (Provenance, Audit, Forget).
- **Performance** (Oxigraph, O(1) counting).

Pour tester SmartMemory et voir ses capacités neuro-symboliques en action, voici une séquence de phrases à saisir. Ces exemples sont conçus pour forcer le LLM à utiliser les outils (add_memory, search_entity, etc.) et déclencher les règles d'inférence.

1. Test de la Recherche Sémantique (Alias SKOS)
Objectif : Montrer que SmartMemory comprend que "S-CSCF" et "Serving Call Session Control Function" sont la même chose.

Saisie LLM : Souviens-toi que le S-CSCF est un composant critique de l'IMS.
Vérification : SmartMemory doit utiliser add_memory.
Saisie LLM : Quelles sont les informations sur le Serving Call Session Control Function ?
Attendu : Le LLM doit trouver l'info grâce aux alias SKOS sans que vous ayez explicitement lié les deux termes.
2. Test d'Inférence et de Validation Humaine
Objectif : Déclencher une règle de déduction qui demande confirmation (Human-in-the-loop).

Saisie LLM : Alice travaille chez Thales et Bob est son collègue.
Vérification : SmartMemory doit déduire que Bob travaille probablement aussi chez Thales.
Saisie LLM : Y a-t-il des déductions en attente de vérification ? (Ou utilisez l'outil get_pending_verifications)
Attendu : Il doit vous proposer de confirmer :Bob schema:worksFor :Thales.
3. Test de Détection de Conflit (Contradiction)
Objectif : Voir la réaction du système face à une donnée incohérente.

Saisie LLM : L'âge de Charlie est de 25 ans.
Vérification : Ajout réussi.
Saisie LLM : En fait, Charlie a 30 ans.
Attendu : L'outil add_memory doit répondre avec un avertissement ⚠️ Found potential conflicts! car Charlie ne peut pas avoir deux âges différents (Functional Property).
4. Test de Traçabilité et Audit (Provenance)
Objectif : Savoir exactement "qui" a dit quoi et "quand".

Saisie LLM : Qui a ajouté l'information sur le S-CSCF et à quelle date ?
Attendu : Le LLM utilise search_entity ou interroge la provenance pour vous répondre (Auteur: user, Source: explicit).
5. Test du "Droit à l'Oubli"
Objectif : Vérifier que la suppression est propre et totale.

Saisie LLM : Oublie tout ce que tu sais sur l'âge de Charlie.
Vérification : Le LLM doit appeler forget_memory.
Saisie LLM : Quel est l'âge de Charlie ?
Attendu : "Je ne sais pas", et aucune trace de provenance ne doit subsister dans le graphe.
💡 Conseil pour la démo :
Pour que le LLM soit encore plus efficace, vous pouvez lui donner cette instruction au début de la conversation :

"Utilise tes outils SmartMemory pour stocker et structurer nos connaissances. N'hésite pas à vérifier les inférences automatiques et à me signaler toute contradiction sémantique."
