#!/bin/bash

# Script pour créer et activer un environnement virtuel Python pour Rainfall

VENV_DIR="venv"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Aller dans le répertoire du projet
cd "$PROJECT_DIR"

# Créer le venv s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Environnement virtuel créé"
else
    echo "✓ Environnement virtuel existe déjà"
fi

# Activer le venv
echo "Activation de l'environnement virtuel..."
source "$VENV_DIR/bin/activate"

# Mettre à jour pip
echo "Mise à jour de pip..."
pip install --upgrade pip --quiet

# Installer les dépendances (pwntools est nécessaire pour les exploits)
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances depuis requirements.txt..."
    pip install -r requirements.txt --quiet
else
    echo "Installation de pwntools..."
    pip install pwntools --quiet
fi

echo ""
echo "✓ Environnement virtuel activé et prêt à l'emploi!"
echo "Pour activer manuellement plus tard, utilisez:"
echo "  source $PROJECT_DIR/$VENV_DIR/bin/activate"
echo ""
echo "Pour désactiver, utilisez:"
echo "  deactivate"

