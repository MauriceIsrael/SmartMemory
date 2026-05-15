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

## Test 6 : Raisonnement Asynchrone et "Debouncing"

**Objectif** : Démontrer que le serveur peut traiter des flux de données rapides sans bloquer l'agent, en consolidant les inférences en arrière-plan.

1. **Action** : Envoyer une rafale de faits liés.
   - *Entrée 1* : "Alice travaille chez Thales."
   - *Entrée 2* : "Bob travaille chez Thales."
   - *Entrée 3* : "Charlie travaille chez Thales."
2. **Action** : Observer les logs du serveur.
3. **Résultat attendu** : 
   - Le serveur confirme immédiatement chaque ajout.
   - L'`InferenceManager` attend quelques secondes (debouncing) après le dernier ajout avant de lancer une **unique** passe d'inférence.
   - Une requête `SELECT ?c WHERE { :Alice schema:colleague ?c }` renverra Bob et Charlie quelques instants plus tard, prouvant que le raisonneur travaille en "temps différé intelligent".

---

## Conclusion

SmartMemory n'est pas qu'une base de données RDF ; c'est un **système de gestion de la connaissance active** qui combine :
- **Rigueur sémantique** (Ontologies, SPARQL).
- **Flexibilité LLM** (Extraction, Suggestion).
- **Gouvernance** (Provenance, Audit, Forget).
- **Réactivité** (Inférence Asynchrone, Debouncing).
- **Performance** (Oxigraph, O(1) counting).

