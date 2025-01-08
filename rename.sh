#!/bin/bash

# Vérification si l'argument est passé (le dossier racine)
if [ -z "$1" ]; then
  echo "Usage: $0 <répertoire de base>"
  exit 1
fi

# Le répertoire de base (exemple : /path/to/directory)
BASE_DIR="$1"

# Parcours des répertoires pY/Caméra.X/
for person_dir in "$BASE_DIR"/*; do
  if [[ -d "$person_dir" && "$person_dir" =~ p([0-9]+) ]]; then
    PERSON_ID="${BASH_REMATCH[1]}"

    # Recherche des répertoires Caméra.X dans pY/Caméra.X/
    for camera_dir in "$person_dir"/Caméra.*; do
      if [[ -d "$camera_dir" && "$camera_dir" =~ Caméra\.([0-9]+) ]]; then
        CAMERA_ID="${BASH_REMATCH[1]}"
        
        # Créer le répertoire de destination Camera.X/pY
        DEST_DIR="$BASE_DIR/Camera.$CAMERA_ID/p$PERSON_ID"
        mkdir -p "$DEST_DIR"

        # Copier tous les fichiers .png de Caméra.X_in vers Camera.X/pY/
        SOURCE_DIR="$camera_dir/${camera_dir##*/}_in"
        if [[ -d "$SOURCE_DIR" ]]; then
          cp "$SOURCE_DIR"/*.png "$DEST_DIR/"
          echo "Copie des fichiers de $SOURCE_DIR vers $DEST_DIR"
        fi
      fi
    done
  fi
done
