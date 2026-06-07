"""
Modèles Pydantic pour la validation des données des tâches.

- TodoCreate : ce qu'on envoie pour créer une tâche
- TodoUpdate : ce qu'on envoie pour modifier une tâche (juste completed ici)
- Todo : représentation complète d'une tâche telle qu'elle est renvoyée au client
"""

from pydantic import BaseModel, Field, field_validator


class TodoCreate(BaseModel):
    """
    Schéma attendu lors de la création d'une nouvelle tâche.
    Seul le titre est obligatoire, la priorité est optionnelle (moyenne par défaut).
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Le texte de la tâche à faire"
    )
    priority: str = Field(
        default="moyenne",
        pattern=r"^(haute|moyenne|basse)$",
        description="Niveau de priorité : haute, moyenne ou basse"
    )

    @field_validator("title")
    def title_must_not_be_blank(cls, v: str) -> str:
        """Empêche les titres composés uniquement d'espaces."""
        if not v.strip():
            raise ValueError("Le titre ne peut pas être vide")
        return v.strip()


class TodoUpdate(BaseModel):
    """
    Schéma utilisé pour marquer une tâche comme faite ou non faite.
    Seul le champ 'completed' est modifiable via cet endpoint.
    """
    completed: bool = Field(
        ...,
        description="True si la tâche est terminée, False sinon"
    )


class Todo(BaseModel):
    """
    Représentation complète d'une tâche, telle qu'elle est renvoyée par l'API.
    Les données viennent de SQLite (où 'completed' est 0 ou 1),
    ce modèle les convertit automatiquement en booléen Python.
    """
    id: int
    title: str
    priority: str
    completed: bool
    created_at: str  # format ISO 8601 (chaîne renvoyée par SQLite)

    @field_validator("completed", mode="before")
    def int_to_bool(cls, v) -> bool:
        """Convertit l'entier 0/1 de SQLite en booléen Python."""
        if isinstance(v, int):
            return bool(v)
        if isinstance(v, bool):
            return v
        raise ValueError("completed doit être 0, 1, True ou False")
