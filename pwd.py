import random
import string
import os
import re
import json

#version avec des lettres, des chiffres et des caractères spéciaux
#def generate_random_password(length):
#    """Génère un mot de passe aléatoire avec la longueur spécifiée."""
#    characters = string.ascii_letters + string.digits + string.punctuation
#    return ''.join(random.choice(characters) for _ in range(length))
#////////////////////////////////////////////////////////////////////////////

#Version seulement avec des lettres et des chiffres
def generate_random_password(length):
    """Génère un mot de passe aléatoire avec uniquement des lettres et des chiffres."""
    # N'inclure que les lettres et les chiffres (pas de caractères spéciaux)
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def update_password_in_json_file(filepath, field_name, new_password):
    """
    Met à jour le mot de passe dans un fichier JSON pour le champ donné.
    """
    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        print(f"Le fichier {filepath} n'existe pas.")
        return False
    
    try:
        # Lire le contenu JSON
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Vérifier si le champ existe
        if field_name in data:
            data[field_name] = new_password
            
            # Écrire le contenu JSON mis à jour
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            
            print(f"Le champ {field_name} dans {filepath} a été mis à jour avec le nouveau mot de passe.")
            return True
        else:
            print(f"Le champ {field_name} n'a pas été trouvé dans le fichier JSON {filepath}.")
            return False
    
    except json.JSONDecodeError:
        print(f"Le fichier {filepath} n'est pas un fichier JSON valide.")
        return False
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier JSON {filepath}: {e}")
        return False

def update_password_in_cfg_file(filepath, field_name, new_password, line_number=None, context=None):
    """
    Met à jour le mot de passe dans un fichier .cfg pour le champ donné.
    Les fichiers .cfg utilisent souvent la syntaxe 'field = value' sans guillemets.
    """
    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        print(f"Le fichier {filepath} n'existe pas.")
        return False
    
    try:
        # Lire toutes les lignes du fichier
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Plusieurs formats possibles pour les fichiers .cfg
        patterns = [
            f"{field_name}\\s*=\\s*\"[^\"]*\"",         # format: field = "value"
            f"{field_name}\\s*=\\s*'[^']*'",            # format: field = 'value'
            f"{field_name}\\s*=\\s*[^\\s;#\n]+",        # format: field = value (sans guillemets)
            f"{field_name}\\s+\"[^\"]*\"",              # format: field "value"
            f"{field_name}\\s+'[^']*'",                 # format: field 'value'
            f"{field_name}\\s+[^\\s;#\n]+"              # format: field value (sans guillemets)
        ]
        
        modified = False
        
        # Traiter selon les paramètres fournis
        if line_number is not None:
            # Modifier le mot de passe à une ligne spécifique
            if 1 <= line_number <= len(lines):
                for pattern in patterns:
                    if re.search(pattern, lines[line_number-1]):
                        lines[line_number-1] = re.sub(
                            pattern,
                            f"{field_name} = \"{new_password}\"",
                            lines[line_number-1]
                        )
                        modified = True
                        break
                
                if not modified:
                    print(f"Le champ {field_name} n'a pas été trouvé à la ligne {line_number}.")
            else:
                print(f"Numéro de ligne invalide: {line_number}. Le fichier contient {len(lines)} lignes.")
        
        elif context is not None:
            # Chercher le contexte spécifié
            context_found = False
            for i, line in enumerate(lines):
                if context in line:
                    context_found = True
                    continue
                
                if context_found:
                    for pattern in patterns:
                        if re.search(pattern, line):
                            lines[i] = re.sub(
                                pattern,
                                f"{field_name} = \"{new_password}\"",
                                line
                            )
                            modified = True
                            break
                    
                    if modified:
                        break
            
            if not modified:
                print(f"Le champ {field_name} n'a pas été trouvé après le contexte '{context}'.")
        
        else:
            # Chercher et remplacer la première occurrence du champ dans tout le fichier
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line):
                        lines[i] = re.sub(
                            pattern,
                            f"{field_name} = \"{new_password}\"",
                            line
                        )
                        modified = True
                        break
                
                if modified:
                    break
            
            if not modified:
                print(f"Le champ {field_name} n'a pas été trouvé dans {filepath}.")
                # Option d'ajouter le champ s'il n'existe pas
                print(f"Souhaitez-vous ajouter le champ {field_name} au fichier? (o/n)")
                response = input().lower()
                if response in ['o', 'oui', 'y', 'yes']:
                    lines.append(f"{field_name} = \"{new_password}\"\n")
                    modified = True
                    print(f"Le champ {field_name} a été ajouté au fichier {filepath}.")
        
        if modified:
            # Écrire les lignes modifiées dans le fichier
            with open(filepath, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            
            print(f"Le champ {field_name} dans {filepath} a été mis à jour avec le nouveau mot de passe.")
            return True
        
        return False
    
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier {filepath}: {e}")
        return False

def update_password_in_config_file(filepath, field_name, new_password, line_number=None, context=None):
    """
    Met à jour le mot de passe dans un fichier de configuration standard pour le champ donné.
    """
    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        print(f"Le fichier {filepath} n'existe pas.")
        return False
    
    try:
        # Lire toutes les lignes du fichier
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        pattern = f"{field_name}\\s*=\\s*[\"']?[^\"'\n]*[\"']?"
        modified = False
        
        # Traiter selon les paramètres fournis
        if line_number is not None:
            # Modifier le mot de passe à une ligne spécifique
            if 1 <= line_number <= len(lines):
                if re.search(pattern, lines[line_number-1]):
                    lines[line_number-1] = re.sub(
                        pattern,
                        f"{field_name}=\"{new_password}\"",
                        lines[line_number-1]
                    )
                    modified = True
                else:
                    print(f"Le champ {field_name} n'a pas été trouvé à la ligne {line_number}.")
            else:
                print(f"Numéro de ligne invalide: {line_number}. Le fichier contient {len(lines)} lignes.")
        
        elif context is not None:
            # Chercher le contexte spécifié
            context_found = False
            for i, line in enumerate(lines):
                if context in line:
                    context_found = True
                    continue
                
                if context_found and re.search(pattern, line):
                    lines[i] = re.sub(
                        pattern,
                        f"{field_name}=\"{new_password}\"",
                        line
                    )
                    modified = True
                    break
            
            if not modified:
                print(f"Le champ {field_name} n'a pas été trouvé après le contexte '{context}'.")
        
        else:
            # Chercher et remplacer la première occurrence du champ dans tout le fichier
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    lines[i] = re.sub(
                        pattern,
                        f"{field_name}=\"{new_password}\"",
                        line
                    )
                    modified = True
                    break
            
            if not modified:
                print(f"Le champ {field_name} n'a pas été trouvé dans {filepath}.")
        
        if modified:
            # Écrire les lignes modifiées dans le fichier
            with open(filepath, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            
            print(f"Le champ {field_name} dans {filepath} a été mis à jour avec le nouveau mot de passe.")
            return True
        
        return False
    
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier {filepath}: {e}")
        return False

def is_json_file(filepath):
    """Détermine si un fichier est au format JSON en vérifiant son contenu."""
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            json.load(file)
        return True
    except:
        return False

def is_cfg_file(filepath):
    """Détermine si un fichier est au format .cfg en vérifiant son extension."""
    if not os.path.exists(filepath):
        return False
    
    _, extension = os.path.splitext(filepath)
    return extension.lower() in ['.cfg', '.conf']

def update_password_in_file(filepath, field_name, new_password, line_number=None, context=None):
    """
    Met à jour le mot de passe dans un fichier, détecte automatiquement le type de fichier.
    """
    # Affiche le fichier que nous allons analyser
    print(f"\nAnalyse du fichier {filepath}...")
    
    # Essaie d'afficher les premières lignes du fichier pour aider au diagnostic
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            first_lines = file.readlines()[:10]  # Lire les 10 premières lignes
            print(f"Aperçu du contenu du fichier (10 premières lignes):")
            for i, line in enumerate(first_lines):
                print(f"{i+1}: {line.strip()}")
    except Exception as e:
        print(f"Impossible de lire le fichier pour aperçu: {e}")
    
    # Détermine le type de fichier et utilise la fonction appropriée
    if is_json_file(filepath):
        print("Détecté comme fichier JSON")
        return update_password_in_json_file(filepath, field_name, new_password)
    elif is_cfg_file(filepath):
        print("Détecté comme fichier CFG")
        return update_password_in_cfg_file(filepath, field_name, new_password, line_number, context)
    else:
        print("Type de fichier non détecté, traitement comme fichier de configuration standard")
        return update_password_in_config_file(filepath, field_name, new_password, line_number, context)

def main():
    print("Script de mise à jour de mots de passe dans des fichiers")
    print("------------------------------------------------------")
    
    # Utiliser des backslashes \ pour les chemin sous Windows
    server_file = r"C:\Users\mizer\Desktop\test\server_config.cfg"
    password_file = r"C:\Users\mizer\Desktop\test\config.json"
    
    # Configuration pour server_password launcher spécifier ligne si nécessaire
    server_line = None  # Aucune ligne spécifique
    server_context = None  # Aucun contexte spécifique
    
    # Configuration pour password coté serveur arma spécifier ligne si nécessaire
    password_line = None  # Aucune ligne spécifique
    password_context = None  # Aucun contexte spécifique
    
    # Générer un seul mot de passe qui sera utilisé dans les deux fichiers
    password_length = random.randint(5, 50)  # Longueur aléatoire entre 15 et 20 caractères
    shared_password = generate_random_password(password_length)
    print(f"Nouveau mot de passe généré: {shared_password}")
    
    # Mettre à jour les mots de passe avec le même mot de passe
    update_password_in_file(server_file, "password", shared_password, server_line, server_context)  #nom de la ligne du fichier server
    update_password_in_file(password_file, "server_password", shared_password, password_line, password_context)  #nom de la ligne dans la config launcher

if __name__ == "__main__":
    main()
