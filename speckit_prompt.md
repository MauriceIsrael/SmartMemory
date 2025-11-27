# Prompt pour Speckit.specify : Application de Supervision du Moteur d'Inférence

**Contexte :**
Nous développons une application de "Mémoire Sémantique" (`SmartMemory`) basée sur un graphe de connaissances (RDFLib) et un moteur de règles d'inférence (SPARQL). Le backend est écrit en Python. Nous avons besoin d'une interface web pour superviser ce système, visualiser les faits, contrôler les règles d'inférence et administrer le moteur.

**Objectif :**
Créer une application web complète (Frontend + Backend API léger) pour la supervision.

**Stack Technique :**
*   **Frontend :** SvelteKit (Svelte 5 si possible, sinon 4), TailwindCSS pour le styling (design moderne, "premium", mode sombre).
*   **Backend API :** FastAPI (Python) pour exposer les objets internes du moteur existant via une API REST.

**Fonctionnalités Requises :**

1.  **Backend (FastAPI Bridge) :**
    *   Créer un serveur FastAPI qui importe les instances existantes de `SemanticMemoryServer` (ou initialise un accès partagé au `ProvenanceGraph` et `RuleEngine`).
    *   Endpoints nécessaires :
        *   `GET /stats` : Nombre total de triplets, nombre de règles actives/inactives, nombre de faits inférés vs assertés.
        *   `GET /facts` : Liste paginée des triplets (Sujet, Prédicat, Objet). Filtres par recherche textuelle. Inclusion des métadonnées de provenance (ex: `source="sparql-rule"` vs `source="user"`).
        *   `GET /rules` : Liste des règles d'inférence. Champs : `id`, `description`, `sparql_query`, `is_active`, `execution_count`, `triples_generated`, `validation_error`.
        *   `POST /rules/{id}/toggle` : Activer/Désactiver une règle.
        *   `POST /inference/run` : Déclencher manuellement le moteur d'inférence.

2.  **Frontend (SvelteKit) :**
    *   **Design :** Interface moderne, dashboard type "Admin", sidebar de navigation. Utilisation de composants réactifs.
    *   **Page Dashboard :**
        *   Cartes de statistiques (KPIs) : Total Faits, Faits Inférés (avec pourcentage), Règles Actives.
        *   Graphique simple (optionnel) montrant l'évolution des faits.
    *   **Page "Explorateur de Faits" :**
        *   Tableau interactif des triplets.
        *   Badge visuel pour distinguer les faits "Inférés" (automatiques) des faits "Assertés" (manuels).
        *   Barre de recherche pour filtrer les faits.
    *   **Page "Règles d'Inférence" :**
        *   Liste des règles avec leur état (Actif/Inactif).
        *   Affichage du code SPARQL de la règle (syntax highlighting).
        *   Affichage des statistiques par règle (nombre d'exécutions, triplets générés).
        *   Bouton "Switch" pour activer/désactiver une règle en temps réel.
    *   **Console d'Administration :**
        *   Bouton "Lancer l'Inférence" (avec indicateur de chargement).
        *   Logs en temps réel (si possible, ou derniers logs).

**Instructions Spécifiques :**
*   Le code doit être modulaire.
*   L'interface doit être "Wow" : animations fluides, feedback visuel lors des actions (ex: toast notification quand une règle est activée).
*   Gérer les erreurs de connexion au backend proprement.

**Structure des Données Existante (Référence) :**
*   Les règles sont des objets `InferenceRule` avec les attributs : `id`, `sparql_query`, `is_active`, `execution_count`, `triples_generated`.
*   Le graphe est un `ProvenanceGraph` (RDFLib wrapper).
