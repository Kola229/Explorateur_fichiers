import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter import *
import os
import webbrowser
from PIL import Image, ImageTk
import json
import datetime

# Nom du fichier JSON pour stocker les chemins des favoris
FAVORITES_FILE = "favorites.json"

# Création de la fenêtre principale de l'application
root = tk.Tk()
root.title("Explorateur de fichiers")

# Variables de contrôle pour stocker des informations dynamiques de l'interface
path_var = tk.StringVar()         # Stocke le chemin du répertoire actuel affiché
filter_text_var = tk.StringVar()  # Stocke le texte entré pour filtrer les fichiers
search_text_var = tk.StringVar()  # Stocke le texte entré pour rechercher des fichiers

# Ensemble pour stocker les chemins des fichiers et dossiers favoris (utilisation d'un ensemble pour éviter les doublons)
favorites = set()

# Variable pour suivre la vue actuelle : "files" pour l'explorateur normal, "favorites" pour la liste des favoris
current_view = "files"

# --- Fonction pour charger les favoris depuis le fichier au démarrage ---
try:
    with open(FAVORITES_FILE, "r") as f:
        # Charge le contenu JSON du fichier et le convertit en un ensemble de favoris
        favorites = set(json.load(f))
except FileNotFoundError:
    # Si le fichier de favoris n'existe pas, une exception FileNotFoundError est levée, que nous ignorons.
    # Cela signifie qu'il n'y a pas encore de favoris enregistrés.
    pass

# --- Fonction pour enregistrer les favoris dans le fichier ---
def save_favorites():
    try:
        with open(FAVORITES_FILE, "w") as f:
            # Convertit l'ensemble des favoris en une liste (car JSON ne supporte pas directement les ensembles)
            # et écrit cette liste au format JSON dans le fichier.
            json.dump(list(favorites), f)
    except Exception as e:
        # En cas d'erreur lors de l'enregistrement (par exemple, problème de permissions),
        # affiche une boîte de message d'erreur à l'utilisateur.
        messagebox.showerror("Erreur", f"Impossible d'enregistrer les favoris : {e}")

# --- Chargement des icônes ---
try:
    # Ouvre les fichiers image pour les icônes et les redimensionne à 16x16 pixels.
    folder_img = Image.open("folder.png").resize((16, 16))
    folder_icon = ImageTk.PhotoImage(folder_img)  # Convertit l'image PIL en un format utilisable par Tkinter

    file_img = Image.open("file.png").resize((16, 16))
    file_icon = ImageTk.PhotoImage(file_img)

    fav_img = Image.open("star.png").resize((16, 16))
    fav_icon = ImageTk.PhotoImage(fav_img)
except FileNotFoundError as e:
    # Si un fichier d'icône est introuvable, affiche un message d'erreur et quitte l'application.
    messagebox.showerror("Erreur", f"Fichier d'icône introuvable : {e.filename}")
    root.destroy()
    exit()

# --- Fonction pour ouvrir un dossier et mettre à jour l'interface ---
def open_folder(folder_path):
    if folder_path:
        # Met à jour la variable du chemin actuel
        path_var.set(folder_path)
        # Recrée les "breadcrumbs" (la barre de navigation du chemin) pour le nouveau dossier
        create_breadcrumbs(folder_path)
        if current_view == "files":
            # Si la vue actuelle est celle des fichiers, liste et affiche les fichiers du dossier,
            # en appliquant le filtre si nécessaire, et met à jour la liste dans le listbox.
            list_files(folder_path, filter_text_var.get())
            list_files_in_listbox(folder_path, filter_text_var.get())
            # Efface le panneau d'informations lors du changement de dossier
            clear_info_panel()
        elif current_view == "favorites":
            # Si la vue actuelle est celle des favoris, affiche la liste des favoris.
            list_favorites()
            # Efface le panneau d'informations lors du passage à la vue des favoris
            clear_info_panel()

# --- Fonction pour lister les fichiers et dossiers dans un chemin donné ---
def list_files(folder_path, filter_text=""):
    # Détruit tous les widgets (labels) précédemment affichés dans le frame de la liste de fichiers
    for widget in frame1_inner.winfo_children():
        widget.destroy()
    try:
        # Obtient la liste des éléments (fichiers et dossiers) dans le chemin spécifié
        items = os.listdir(folder_path)
        for i, item in enumerate(items):
            item_path = os.path.join(folder_path, item)  # Crée le chemin complet de l'élément
            if filter_text and filter_text.lower() not in item.lower():
                # Si un texte de filtre est fourni et qu'il n'est pas présent (en minuscules) dans le nom de l'élément,
                # on passe à l'élément suivant (le filtre est appliqué).
                continue
            # Choisir l'icône appropriée en fonction du type de l'élément
            if os.path.isdir(item_path):
                icon = folder_icon
            else:
                icon = file_icon

            # Création d'un label pour chaque élément avec son nom, une icône et un curseur "main" au survol
            label = tk.Label(frame1_inner, text=item, cursor="hand2", image=icon, compound=tk.LEFT)
            # Positionne le label dans la grille
            label.grid(row=i, column=0, sticky="ew", padx=2, pady=1)
            # Lie un clic gauche sur le label à la fonction on_item_click
            label.bind("<Button-1>", lambda e, p=item_path, l=label: on_item_click(p, l))
            # Lie un clic droit sur le label à la fonction show_context_menu
            label.bind("<Button-3>", lambda event, p=item_path, l=label: show_context_menu(event, p, l))
        # Configure la colonne de la grille pour qu'elle s'étire avec la fenêtre
        frame1_inner.grid_columnconfigure(0, weight=1)
    except Exception as e:
        # En cas d'erreur lors de la listage des fichiers (par exemple, permissions refusées),
        # affiche une boîte de message d'erreur.
        messagebox.showerror("Erreur", str(e))

# --- Fonction pour lister les favoris ---
def list_favorites():
    # Détruit tous les widgets précédemment affichés dans le frame de la liste de fichiers
    for widget in frame1_inner.winfo_children():
        widget.destroy()
    i = 0
    for fav_path in favorites:
        if os.path.exists(fav_path):
            item = os.path.basename(fav_path)
            if os.path.isdir(fav_path):
                icon = folder_icon
            else:
                icon = fav_icon  # Utilise l'icône de favori pour la liste des favoris
            label = tk.Label(frame1_inner, text=item, cursor="hand2", image=icon, compound=tk.LEFT)
            label.grid(row=i, column=0, sticky="ew", padx=2, pady=1)
            label.bind("<Button-1>", lambda e, p=fav_path, l=label: on_item_click(p, l))
            label.bind("<Button-3>", lambda event, p=fav_path, l=label: show_context_menu(event, p, l))
            i += 1
    frame1_inner.grid_columnconfigure(0, weight=1)

# --- Fonction appelée lors d'un clic sur un élément de la liste ---
def on_item_click(item_path, clicked_label):
    # Réinitialise la couleur de fond des autres labels de la liste
    for widget in frame1_inner.winfo_children():
        if isinstance(widget, tk.Label) and widget.winfo_exists() and widget != clicked_label:
            widget.config(bg=root.cget('bg'))

    if os.path.isdir(item_path):
        # Si l'élément cliqué est un dossier, change sa couleur de fond et l'ouvre après un court délai
        clicked_label.config(bg="lightblue")
        root.after(10, lambda: open_folder(item_path))
        # Affiche les informations du dossier
        display_info(item_path)
    else:
        # Si l'élément cliqué est un fichier, met à jour la variable du chemin actuel,
        # change sa couleur de fond et affiche ses informations.
        path_var.set(item_path)
        clicked_label.config(bg="lightgreen")
        display_info(item_path)

# --- Fonction pour créer les "breadcrumbs" (la barre de navigation du chemin) ---
def create_breadcrumbs(path):
    # Détruit tous les labels précédemment affichés dans le frame des breadcrumbs
    for widget in frame2.winfo_children():
        widget.destroy()
    # Divise le chemin en ses différents segments
    segments = path.split(os.sep)
    for i, segment_name in enumerate(segments):
        # Reconstitue le chemin jusqu'au segment actuel
        segment = os.sep.join(segments[:i+1])
        # Crée un label pour le segment avec un style cliquable
        label = tk.Label(frame2, text=segment_name, cursor="hand2", fg="blue")
        label.grid(row=0, column=i * 2, sticky='w', padx=2)
        # Lie un clic gauche sur le label à la fonction on_breadcrumb_click
        label.bind("<Button-1>", lambda e, p=segment: on_breadcrumb_click(p))
        if i < len(segments) - 1:
            # Ajoute un séparateur (le caractère du séparateur de chemin) entre les segments
            separator_label = tk.Label(frame2, text=os.sep)
            separator_label.grid(row=0, column=i * 2 + 1, sticky='w')

# --- Fonction appelée lors d'un clic sur un "breadcrumb" ---
def on_breadcrumb_click(path):
    # Ouvre le dossier correspondant au "breadcrumb" cliqué
    open_folder(path)

# --- Fonction pour ajouter ou retirer un élément des favoris ---
def toggle_favorite(item_path, clicked_label):
    if item_path in favorites:
        # Si le chemin est déjà dans les favoris, le retire
        favorites.remove(item_path)
        # TODO: Trouver un moyen de mettre à jour l'icône dans la liste si elle est visible
    else:
        # Si le chemin n'est pas dans les favoris, l'ajoute
        favorites.add(item_path)
        # TODO: Trouver un moyen de mettre à jour l'icône dans la liste si elle est visible
    # Enregistre les favoris mis à jour dans le fichier
    save_favorites()
    if current_view == "favorites":
        # Si la vue des favoris est active, la réaffiche pour refléter le changement
        list_favorites()
    elif current_view == "files":
        # Si la vue des fichiers est active, réouvre le dossier actuel pour potentiellement mettre à jour l'affichage
        open_folder(path_var.get())

# --- Fonction pour afficher le menu contextuel lors d'un clic droit ---
def show_context_menu(event, item_path, clicked_label):
    # Création du menu contextuel
    context_menu = tk.Menu(root, tearoff=0)

    if os.path.isfile(item_path):
        # Si l'élément est un fichier, ajoute une option pour l'ouvrir
        context_menu.add_command(label="Ouvrir", command=lambda p=item_path: open_file(p))
    else:
        # Si l'élément est un dossier, ajoute une option pour l'ouvrir (explorer)
        context_menu.add_command(label="Ouvrir", command=lambda p=item_path: open_folder(p))

    # Vérifie si l'élément est déjà dans les favoris pour adapter le texte de l'option
    is_favorite = item_path in favorites
    fav_label = "Retirer des favoris" if is_favorite else "Ajouter aux favoris"
    # Ajoute une option pour gérer les favoris
    context_menu.add_command(label=fav_label, command=lambda p=item_path, l=clicked_label: toggle_favorite(p, l))
    # Ajoute une option pour renommer l'élément
    context_menu.add_command(label="Renommer", command=lambda p=item_path, l=clicked_label: rename_item(p, l))
    # Ajoute une option pour supprimer l'élément
    context_menu.add_command(label="Supprimer", command=lambda p=item_path, l=clicked_label: delete_item(p, l))

    try:
        # Affiche le menu contextuel à la position du clic droit
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        # Assure que le menu contextuel est bien relâché après utilisation
        context_menu.grab_release()

# --- Fonction pour ouvrir un fichier avec l'application par défaut ---
def open_file(file_path):
    try:
        webbrowser.open(file_path)
    except Exception as e:
        # En cas d'erreur lors de l'ouverture du fichier, affiche un message d'erreur.
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

# --- Fonction pour supprimer un fichier ou un dossier ---
def delete_item(item_path, clicked_label):
    if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer '{os.path.basename(item_path)}' ?"):
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)  # Supprime le fichier
            else:
                os.rmdir(item_path)   # Supprime le dossier (doit être vide)
            messagebox.showinfo("Succès", f"'{os.path.basename(item_path)}' a été supprimé.")
            # Réouvre le dossier parent pour mettre à jour l'affichage
            open_folder(os.path.dirname(item_path))
            # Retire l'élément des favoris s'il y était
            if item_path in favorites:
                favorites.remove(item_path)
                save_favorites()
        except OSError as e:
            # En cas d'erreur lors de la suppression (par exemple, permissions refusées, dossier non vide),
            # affiche un message d'erreur.
            messagebox.showerror("Erreur", f"Impossible de supprimer '{os.path.basename(item_path)}' : {e}")

# --- Fonction pour renommer un fichier ou un dossier ---
def rename_item(item_path, clicked_label):
    current_name = os.path.basename(item_path)
    # Ouvre une boîte de dialogue pour demander le nouveau nom
    new_name = simpledialog.askstring("Renommer", f"Nouveau nom pour '{current_name}':", initialvalue=current_name)
    if new_name:
        if new_name == current_name:
            return  # Ne fait rien si le nouveau nom est le même que l'ancien
        parent_dir = os.path.dirname(item_path)
        new_path = os.path.join(parent_dir, new_name)
        try:
            os.rename(item_path, new_path)  # Renomme l'élément
            messagebox.showinfo("Succès", f"'{current_name}' a été renommé en '{new_name}'.")
            # Met à jour les favoris si l'élément renommé était un favori
            if item_path in favorites:
                favorites.remove(item_path)
                favorites.add(new_path)
                save_favorites()
            # Réouvre le dossier parent pour mettre à jour l'affichage
            open_folder(parent_dir)
        except FileExistsError:
            # Affiche une erreur si le nouveau nom existe déjà dans le répertoire
            messagebox.showerror("Erreur", f"Le nom '{new_name}' existe déjà dans ce répertoire.")
        except OSError as e:
            # Affiche une erreur en cas de problème lors du renommage (par exemple, permissions refusées)
            messagebox.showerror("Erreur", f"Impossible de renommer '{current_name}' : {e}")

# --- Fonction pour créer un nouveau dossier ---
def create_new_folder():
    current_dir = path_var.get() if path_var.get() else os.path.expanduser("~")
    # Ouvre une boîte de dialogue pour demander le nom du nouveau dossier
    new_folder_name = simpledialog.askstring("Nouveau dossier", "Nom du nouveau dossier :")
    if new_folder_name:
        new_folder_path = os.path.join(current_dir, new_folder_name)
        try:
            os.mkdir(new_folder_path)  # Crée le nouveau dossier
            messagebox.showinfo("Succès", f"Dossier '{new_folder_name}' créé avec succès dans '{current_dir}'.")
            # Réouvre le dossier actuel pour afficher le nouveau dossier
            open_folder(current_dir)
        except OSError as e:
            # Affiche une erreur en cas de problème lors de la création du dossier (par exemple, permissions refusées)
            messagebox.showerror("Erreur", f"Impossible de créer le dossier '{new_folder_name}' : {e}")

# --- Fonction pour appliquer le filtre sur la liste des fichiers ---
def apply_filter():
    # Réouvre le dossier actuel pour réappliquer le filtre
    open_folder(path_var.get() if path_var.get() else os.path.expanduser("~"))
    # Reliste les fichiers en appliquant le texte de filtre
    list_files(path_var.get(), filter_text_var.get())
    # Met également à jour la liste dans le listbox avec le filtre
    list_files_in_listbox(path_var.get(), filter_text_var.get())
    # Efface le panneau d'informations après le filtrage
    clear_info_panel()

# --- Fonction pour actualiser la liste des fichiers ---
def refresh_files():
    # Réouvre le dossier actuel pour forcer une actualisation de la liste
    current_path = path_var.get() if path_var.get() else os.path.expanduser("~")
    open_folder(current_path)
    # Efface le panneau d'informations lors de l'actualisation
    clear_info_panel()

# --- Fonction pour afficher la liste des favoris ---
def show_favorites():
    global current_view
    # Met à jour la variable de la vue actuelle
    current_view = "favorites"
    # Met à jour le chemin affiché à "Favorites"
    path_var.set("Favorites")
    # Recrée les breadcrumbs pour indiquer la vue des favoris
    create_breadcrumbs("Favorites")
    # Liste et affiche les favoris
    list_favorites()
    # Efface le panneau d'informations
    clear_info_panel()

# --- Fonction pour lister les fichiers dans le Listbox (partie droite de l'interface) ---
def list_files_in_listbox(folder_path, filter_text=""):
    # Efface tous les éléments actuellement présents dans le listbox
    listbox.delete(0, tk.END)
    try:
        # Obtient la liste des éléments dans le chemin spécifié
        items = os.listdir(folder_path)
        for item in items:
            item_path = os.path.join(folder_path, item)
            if filter_text and filter_text.lower() not in item.lower():
                continue
            # Insère le nom de l'élément dans le listbox
            listbox.insert(tk.END, item)
    except Exception as e:
        # Affiche une erreur en cas de problème lors du listage pour le listbox
        messagebox.showerror("Erreur", str(e))

# --- Fonction appelée lors d'un double-clic sur un élément du Listbox ---
def on_double_click_listbox(event):
    # Obtient l'index de l'élément sélectionné dans le listbox
    selected_item_index = listbox.curselection()
    if selected_item_index:
        # Obtient le nom de l'élément sélectionné
        selected_item = listbox.get(selected_item_index[0])
        # Reconstitue le chemin complet de l'élément
        current_path = path_var.get() if path_var.get() else os.path.expanduser("~")
        item_path = os.path.join(current_path, selected_item)
        if os.path.isdir(item_path):
            # Si l'élément est un dossier, l'ouvre
            open_folder(item_path)
        else:
            # Si l'élément est un fichier, tente de l'ouvrir
            open_file(item_path)

# --- Fonction pour rechercher des fichiers ---
def search_file():
    # Obtient le texte de recherche en minuscules
    search_text = search_text_var.get().lower()
    # Obtient le chemin actuel
    current_path = path_var.get() if path_var.get() else os.path.expanduser("~")
    # Reliste les fichiers en appliquant le texte de recherche comme filtre
    list_files(current_path, search_text)
    # Met également à jour la liste dans le listbox avec les résultats de la recherche
    list_files_in_listbox(current_path, search_text)
    # Efface le panneau d'informations après la recherche
    clear_info_panel()

# --- Fonction pour afficher les informations d'un fichier ou dossier sélectionné ---
def display_info(item_path):
    # Efface le contenu précédent du panneau d'informations
    clear_info_panel()
    try:
        row = 0
        # Affiche le nom de l'élément en gras comme titre
        info_label = tk.Label(info_frame, text=f"Informations sur : {os.path.basename(item_path)}", font=("Arial", 10, "bold"))
        info_label.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        row += 1

        # Obtient les informations statistiques du fichier ou dossier
        stat_info = os.stat(item_path)

        # Taille
        size_bytes = stat_info.st_size
        size_readable = get_readable_size(size_bytes)
        size_label_text = tk.Label(info_frame, text="Taille :")
        size_label_text.grid(row=row, column=0, padx=5, sticky="w")
        size_label = tk.Label(info_frame, text=size_readable)
        size_label.grid(row=row, column=1, padx=5, sticky="w")
        row += 1

        # Date de création
        creation_time_text = tk.Label(info_frame, text="Créé le :")
        creation_time_text.grid(row=row, column=0, padx=5, sticky="w")
        creation_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        creation_label = tk.Label(info_frame, text=creation_time)
        creation_label.grid(row=row, column=1, padx=5, sticky="w")
        row += 1

        # Date de modification
        modified_time_text = tk.Label(info_frame, text="Modifié le :")
        modified_time_text.grid(row=row, column=0, padx=5, sticky="w")
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        modified_label = tk.Label(info_frame, text=modified_time)
        modified_label.grid(row=row, column=1, padx=5, sticky="w")
        row += 1

        # Type
        type_label_text = tk.Label(info_frame, text="Type :")
        type_label_text.grid(row=row, column=0, padx=5, sticky="w")
        if os.path.isfile(item_path):
            type_label = tk.Label(info_frame, text="Fichier")
            type_label.grid(row=row, column=1, padx=5, sticky="w")
            row += 1
        elif os.path.isdir(item_path):
            type_label = tk.Label(info_frame, text="Dossier")
            type_label.grid(row=row, column=1, padx=5, sticky="w")
            row += 1
            # Nombre d'éléments dans le dossier
            try:
                num_items_text = tk.Label(info_frame, text="Contenu :")
                num_items_text.grid(row=row, column=0, padx=5, sticky="w")
                num_items = len(os.listdir(item_path))
                items_label = tk.Label(info_frame, text=f"{num_items} éléments")
                items_label.grid(row=row, column=1, padx=5, sticky="w")
                row += 1
            except OSError as e:
                items_label_text = tk.Label(info_frame, text="Contenu :")
                items_label_text.grid(row=row, column=0, padx=5, sticky="w")
                items_label = tk.Label(info_frame, text="Accès refusé")
                items_label.grid(row=row, column=1, padx=5, sticky="w")
                row += 1

    except FileNotFoundError:
        err_label = tk.Label(info_frame, text="Impossible de récupérer les informations (fichier non trouvé).", fg="red")
        err_label.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky="w")
    except OSError as e:
        err_label = tk.Label(info_frame, text=f"Impossible de récupérer les informations (accès refusé).", fg="red")
        err_label.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky="w")
    except Exception as e:
        err_label = tk.Label(info_frame, text=f"Erreur lors de la récupération des informations : {e}", fg="red")
        err_label.grid(row=row, column=0, columnspan=2, pady=5, padx=5, sticky="w")

# --- Fonction pour effacer le contenu du panneau d'informations ---
def clear_info_panel():
    # Détruit tous les widgets enfants du frame d'informations
    for widget in info_frame.winfo_children():
        widget.destroy()

# --- Fonction pour convertir la taille en octets en une format lisible (Ko, Mo, Go) ---
def get_readable_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} octets"
    elif size_bytes < (1024 * 1024):
        return f"{size_bytes / 1024:.2f} Ko"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} Mo"

# --- Configuration de la mise en page de la fenêtre principale ---
content = tk.Frame(root, relief="solid", borderwidth=2)
content.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# --- Frame pour la liste de gauche (arborescence des fichiers) ---
left_frame = ttk.Frame(content, relief="solid", borderwidth=1)
left_frame.grid(row=0, column=0, sticky="nsw")
left_frame.grid_rowconfigure(2, weight=1) # Permet à la zone de la liste de s'étendre verticalement

# Bouton "Favoris"
favorites_button = tk.Button(left_frame, text="Favorites", command=show_favorites, image=fav_icon, compound=tk.LEFT)
favorites_button.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

# Frame pour la recherche
search_frame = ttk.Frame(left_frame, relief="solid", borderwidth=1)
search_frame.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
search_entry = tk.Entry(search_frame, textvariable=search_text_var)
search_entry.grid(row=0, column=0, sticky="ew")
search_button = tk.Button(search_frame, text="Rechercher", command=search_file)
search_button.grid(row=0, column=1, sticky="ew")
search_frame.grid_columnconfigure(0, weight=1)

# Zone scrollable pour la liste des fichiers (gauche)
canvas_frame1 = tk.Canvas(left_frame)
scrollbar_frame1 = ttk.Scrollbar(left_frame, orient="vertical", command=canvas_frame1.yview)
scrollable_frame1 = ttk.Frame(canvas_frame1)
scrollable_frame1.bind("<Configure>", lambda e: canvas_frame1.configure(scrollregion=canvas_frame1.bbox("all")))
canvas_frame1.create_window((0, 0), window=scrollable_frame1, anchor="nw")
canvas_frame1.configure(yscrollcommand=scrollbar_frame1.set)
canvas_frame1.grid(row=2, column=0, sticky="nsew")
scrollbar_frame1.grid(row=2, column=1, sticky="ns")
frame1_inner = scrollable_frame1 # Frame interne pour organiser les éléments en grille

# Frame pour la partie droite (liste détaillée)
right_frame = ttk.Frame(content, relief="solid", borderwidth=1)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.grid_rowconfigure(1, weight=1)
content.grid_columnconfigure(1, weight=1)

# Frame pour la barre de chemin (breadcrumbs) en haut à droite
frame2 = ttk.Frame(right_frame, relief="solid", borderwidth=2, height=25)
frame2.grid(row=0, column=0, sticky="ew")
refresh_button = tk.Button(content, text="Actualiser", command=refresh_files)
refresh_button.grid(row=5, column=6,sticky="n,e")
frame2.grid_columnconfigure(0, weight=1)

# Frame pour la liste principale (Listbox) en bas à droite
frame3 = ttk.Frame(right_frame, relief="solid", borderwidth=2)
frame3.grid(row=1, column=0, sticky="nsew")
listbox = tk.Listbox(frame3, height=23, width=120)
listbox.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_rowconfigure(0, weight=1)

# Frame pour les contrôles (filtre, nouveau dossier) en bas à gauche
frame4 = ttk.Frame(left_frame, relief="solid", borderwidth=2)
frame4.grid(row=3,column=0, sticky="ew")
filter_label = tk.Label(frame4, text="Filtrer:")
filter_label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
filter_entry = tk.Entry(frame4, width=20, textvariable=filter_text_var)
filter_entry.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
filter_button = tk.Button(frame4, text="Appliquer le Filtrage", command=apply_filter)
filter_button.grid(row=2, column=0, padx=2, pady=2, sticky="ew")
new_folder_button = tk.Button(frame4, text="Nouveau dossier", command=create_new_folder)
new_folder_button.grid(row=3, column=0, padx=2, pady=2, sticky="ew")

# Frame pour les informations de l'élément sélectionné en bas à gauche
info_frame = ttk.LabelFrame(left_frame, text="Informations", borderwidth=2)
info_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

# Lie le double-clic sur le Listbox à la fonction on_double_click_listbox
listbox.bind("<Double-Button-1>", on_double_click_listbox)

# Ouvre le dossier utilisateur par défaut au démarrage
open_folder(os.path.expanduser("~"))
# Affiche également les informations du dossier utilisateur au démarrage
display_info(os.path.expanduser("~"))

# Lance la boucle principale de l'application Tkinter
root.mainloop()
