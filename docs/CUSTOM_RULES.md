# Guide de Création de Règles SPARQL Personnalisées

SmartMemory permet aux utilisateurs d'ajouter leurs propres règles d'inférence pour créer un **système expert personnalisé**.

## Format des Règles

Les règles SPARQL utilisent le format `CONSTRUCT` pour déduire de nouveaux triplets :

```sparql
# Description de la règle (optionnelle)
CONSTRUCT {
    # Triplets à créer
    ?sujet ?prédicat ?objet .
}
WHERE {
    # Conditions à vérifier
    ?sujet ?propriété ?valeur .
}
```

## Préfixes Automatiques

**Vous n'avez PAS besoin de déclarer les préfixes courants.** Le système ajoute automatiquement :

- `:` → `<http://semanticmemory.org/user#>` (vos entités)
- `rdf:` → RDF standard
- `rdfs:` → RDF Schema
- `foaf:` → Friend of a Friend
- `schema:` → Schema.org
- `owl:` → OWL ontology
- `skos:` → SKOS

## Exemples de Règles

### 1. Règle Métier Simple
**"Les ingénieurs travaillent sur des projets techniques."**

```sparql
CONSTRUCT {
    ?person :worksOn ?project .
}
WHERE {
    ?person rdf:type :Engineer .
    ?project rdf:type :TechnicalProject .
}
```

### 2. Règle de Sécurité (Votre Exemple)
**"Les flux IP de haute sécurité nécessitent TLS."**

```sparql
CONSTRUCT {
    ?flow :requiresEncryption :TLS .
}
WHERE {
    ?flow rdf:type :IPFlow .
    ?flow :securityLevel :High .
}
```

### 3. Règle avec Filtre
**"Les personnes de plus de 65 ans sont des seniors."**

```sparql
CONSTRUCT {
    ?person rdf:type :Senior .
}
WHERE {
    ?person :age ?age .
    FILTER(?age >= 65)
}
```

## Chargement via l'API

### Méthode 1 : Via l'Outil MCP `load_custom_rule`

```python
# L'agent peut appeler directement :
await load_custom_rule({
    "rule_id": "security_tls_rule",
    "rule_content": """
        CONSTRUCT { ?flow :requiresEncryption :TLS . }
        WHERE {
            ?flow rdf:type :IPFlow .
            ?flow :securityLevel :High .
        }
    """,
    "description": "High security flows require TLS"
})
```

### Méthode 2 : Fichier dans `user_rules/`

Créez un fichier `.rq` dans le dossier des règles utilisateur (par défaut : `~/.config/semantic-memory/rules/`).

**Exemple** : `~/.config/semantic-memory/rules/my_security_rules.rq`

```sparql
# TLS requirement for high-security IP flows
CONSTRUCT {
    ?flow :requiresEncryption :TLS .
}
WHERE {
    ?flow rdf:type :IPFlow .
    ?flow :securityLevel :High .
}
```

Le serveur chargera automatiquement cette règle au démarrage.

## Bonnes Pratiques

1. **Nommage explicite** : Utilisez des IDs clairs (`security_tls_rule`, pas `rule1`).
2. **Documentation** : Ajoutez toujours une description en commentaire.
3. **Test progressif** : Commencez simple, puis ajoutez des conditions.
4. **Évitez les boucles** : N'inférez pas des triplets qui vont eux-mêmes déclencher la règle.
5. **Utilisez FILTER NOT EXISTS** : Pour éviter de régénérer des triplets existants.

## Vérification

Après ajout d'une règle, vérifiez qu'elle s'est chargée avec :

```python
await list_rules({})  # Liste toutes les règles actives
```

Puis testez l'inférence :

```python
# Ajouter un fait de base
await add_memory({"input": "Flow1 is an IPFlow with High security"})

# Vérifier l'inférence
await query_memory({"query": "ASK { :Flow1 :requiresEncryption :TLS }"})
# Devrait retourner "True"
```

## Dépannage

| Problème | Solution |
|----------|----------|
| `Error validating rule: SPARQL syntax error` | Vérifiez la syntaxe SPARQL (virgules, points, accolades) |
| `Rule with ID 'xxx' already exists` | Choisissez un ID unique ou supprimez l'ancienne règle |
| `Query did not return a graph` | Utilisez `CONSTRUCT`, pas `SELECT` |
| Inférence ne se déclenche pas | Vérifiez que les triplets de base existent avec `query_memory` |

## Règles Avancées

Pour des règles plus complexes (avec `UNION`, `OPTIONAL`, chemins de propriétés), consultez la [documentation SPARQL 1.1](https://www.w3.org/TR/sparql11-query/).
