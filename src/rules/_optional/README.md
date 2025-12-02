# Règles SPARQL Optionnelles (Basées sur Ontologies OWL)

Ce dossier contient des règles SPARQL génériques qui s'appuient sur les définitions OWL des ontologies (Schema.org, FOAF, etc.).

## Pourquoi ces règles sont désactivées par défaut ?

**Problème de performance** : Ces règles nécessitent le chargement de ~17,000 triplets d'ontologies, ce qui :
- Ralentit le démarrage du serveur (5-10 secondes)
- Augmente la consommation mémoire
- Peut causer des timeouts lors de l'inférence

**Alternative** : Les règles spécifiques dans `defaults/` hardcodent les propriétés (ex: `social_symmetry.rq`) et sont plus rapides.

## Règles disponibles

- `core_symmetry.rq` : Inférence de symétrie générique via `owl:SymmetricProperty`
- `core_transitivity.rq` : Inférence de transitivité générique via `owl:TransitiveProperty`
- `core_inverse.rq` : Inférence de relations inverses via `owl:inverseOf`
- `core_hierarchy.rq` : Inférence de hiérarchie de classes via `rdfs:subClassOf`

## Comment réactiver ces règles ?

### Étape 1 : Activer le chargement des ontologies

Dans `src/semantic_memory/config.py`, modifier :
```python
load_ontologies: bool = True  # Changer False → True
```

### Étape 2 : Déplacer les règles

Copier les fichiers `.rq` de ce dossier vers `defaults/` :
```bash
cp src/rules/_optional/core_*.rq src/rules/defaults/
```

### Étape 3 : Redémarrer le serveur

Le serveur chargera maintenant les ontologies au démarrage.

## Trade-offs

| Aspect | Avec Ontologies | Sans Ontologies |
|--------|----------------|-----------------|
| Démarrage | ~5-10s | <1s |
| Mémoire | ~50 MB | ~5 MB |
| Règles | Génériques | Spécifiques |
| Inférence | Plus lente | Plus rapide |
| Flexibilité | Haute (nouvelles propriétés auto-détectées) | Faible (doit coder chaque propriété) |

**Recommandation** : N'activer que si vous avez besoin de règles génériques pour de nombreuses propriétés OWL.
