import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# erste Python Programm

class VOBildTool:
    def __init__(self, root):
        self.root = root
        self.root.title("VO Bildausrichtungs-Werkzeug - Schritt 1")
        self.root.geometry("1400x900")
        self.root.state("zoomed")

        self.image_files = []
        self.current_index = 0
        self.current_folder = None
        self.current_pil_image = None
        self.current_tk_image = None
        self.rotation_map = {}

        self.allowed_extensions = (".gif", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")

        self.build_ui()
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Left>", self.previous_image)
        self.root.bind("r", self.rotate_right)
        self.root.bind("l", self.rotate_left)
        self.root.bind("u", self.rotate_180)
        self.root.bind("0", self.reset_rotation)

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.btn_open_folder = tk.Button(
            top_frame,
            text="Ordner öffnen",
            command=self.open_folder,
            width=20
        )
        self.btn_open_folder.pack(side=tk.LEFT)

        self.btn_next = tk.Button(
            top_frame,
            text="Nächstes →",
            command=self.next_image,
            width=15
        )
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.btn_prev = tk.Button(
            top_frame,
            text="← Vorheriges",
            command=self.previous_image,
            width=15
        )
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_rotate_right = tk.Button(
            top_frame,
            text="Rechts ⟳",
            command=self.rotate_right,
            width=15
        )
        self.btn_rotate_right.pack(side=tk.LEFT, padx=5)

        self.btn_rotate_left = tk.Button(
            top_frame,
            text="Links ⟲",
            command=self.rotate_left,
            width=15
        )
        self.btn_rotate_left.pack(side=tk.LEFT, padx=5)

        self.btn_rotate_180 = tk.Button(
            top_frame,
            text="180°",
            command=self.rotate_180,
            width=10
        )
        self.btn_rotate_180.pack(side=tk.LEFT, padx=5)

        self.btn_reset = tk.Button(
            top_frame,
            text="Reset",
            command=self.reset_rotation,
            width=10
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        self.btn_save = tk.Button(
            top_frame,
            text="Speichern",
            command=self.save_images,
            width=12
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.lbl_folder = tk.Label(
            top_frame,
            text="Kein Ordner gewählt",
            anchor="w"
        )
        self.lbl_folder.pack(side=tk.LEFT, padx=10)

        info_frame = tk.Frame(self.root)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))

        self.lbl_file = tk.Label(
            info_frame,
            text="Keine Datei geladen",
            anchor="w"
        )
        self.lbl_file.pack(side=tk.TOP, fill=tk.X)

        self.lbl_count = tk.Label(
            info_frame,
            text="Bild 0 von 0",
            anchor="w"
        )
        self.lbl_count.pack(side=tk.TOP, fill=tk.X)

        self.image_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.image_label = tk.Label(self.image_frame, text="Noch kein Bild geladen")
        self.image_label.pack(expand=True)

        self.root.bind("<Configure>", self.on_window_resize)

    def open_folder(self):
        folder = filedialog.askdirectory(title="Bildordner auswählen")

        if not folder:
            return

        self.current_folder = folder
        self.lbl_folder.config(text=folder)

        self.load_images_from_folder(folder)

    def load_images_from_folder(self, folder):
        files = []

        try:
            for file_name in os.listdir(folder):
                full_path = os.path.join(folder, file_name)

                if os.path.isfile(full_path) and file_name.lower().endswith(self.allowed_extensions):
                    files.append(full_path)

            files.sort()

            self.image_files = files
            self.current_index = 0

            if not self.image_files:
                self.current_pil_image = None
                self.current_tk_image = None
                self.image_label.config(image="", text="Keine Bilddateien im Ordner gefunden")
                self.lbl_file.config(text="Keine Datei geladen")
                self.lbl_count.config(text="Bild 0 von 0")
                messagebox.showinfo("Hinweis", "Im gewählten Ordner wurden keine unterstützten Bilddateien gefunden.")
                return

            self.show_current_image()

        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geladen werden:\n{e}")

    def show_current_image(self):
        if not self.image_files:
            return

        image_path = self.image_files[self.current_index]

        try:
            image = Image.open(image_path)
            self.current_pil_image = image

            self.update_image_preview()

            file_name = os.path.basename(image_path)
            self.lbl_file.config(text=f"Datei: {file_name}")
            path = self.image_files[self.current_index]
            rotation = self.rotation_map.get(path, 0)

            self.lbl_count.config(
            text=f"Bild {self.current_index + 1} von {len(self.image_files)}   |   Drehung: {rotation}°"
            )

        except Exception as e:
            messagebox.showerror("Fehler", f"Bild konnte nicht geöffnet werden:\n{e}")

    def update_image_preview(self):
        if self.current_pil_image is None:
            return

        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()

        if frame_width < 50 or frame_height < 50:
            return

        path = self.image_files[self.current_index]
        rotation = self.rotation_map.get(path, 0)

        image_copy = self.current_pil_image.copy().rotate(rotation, expand=True)
        image_copy.thumbnail((frame_width - 20, frame_height - 20))

        self.current_tk_image = ImageTk.PhotoImage(image_copy)
        self.image_label.config(image=self.current_tk_image, text="")
        path = self.image_files[self.current_index]
        rotation = self.rotation_map.get(path, 0)
        self.lbl_count.config(text=f"Bild {self.current_index + 1} von {len(self.image_files)}   |   Drehung: {rotation}°")

    def on_window_resize(self, event):
        if self.current_pil_image is not None:
            self.update_image_preview()

    def next_image(self, event=None):

        if not self.image_files:
            return

        if self.current_index < len(self.image_files) - 1:
         self.current_index += 1
         self.show_current_image()


    def previous_image(self, event=None):

        if not self.image_files:
          return

        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

    def rotate_right(self, event=None):

        if not self.image_files:
            return

        path = self.image_files[self.current_index]

        current_rotation = self.rotation_map.get(path, 0)
        new_rotation = (current_rotation + 270) % 360

        self.rotation_map[path] = new_rotation

        self.update_image_preview()

    def rotate_left(self, event=None):

        if not self.image_files:
            return

        path = self.image_files[self.current_index]

        current_rotation = self.rotation_map.get(path, 0)
        new_rotation = (current_rotation + 90) % 360

        self.rotation_map[path] = new_rotation

        self.update_image_preview()

    def rotate_180(self, event=None):

        if not self.image_files:
          return

        path = self.image_files[self.current_index]

        current_rotation = self.rotation_map.get(path, 0)
        new_rotation = (current_rotation + 180) % 360

        self.rotation_map[path] = new_rotation

        self.update_image_preview()

    def reset_rotation(self, event=None):

        if not self.image_files:
           return

        path = self.image_files[self.current_index]

        self.rotation_map[path] = 0

        self.update_image_preview()

    def save_images(self):

        target_folder = filedialog.askdirectory(title="Zielordner auswählen")

        if not target_folder:
            return

        changed_images = []

        for path, rotation in self.rotation_map.items():
            if rotation != 0:
                changed_images.append((path, rotation))

        if not changed_images:
            messagebox.showinfo("Speichern", "Keine gedrehten Bilder vorhanden.")
            returngit remote add origin https://github.com/rkluecki/vo-bildtool.git

        answer = messagebox.askyesno(
            "Bestätigung",
            f"{len(changed_images)} Bilder wirklich überschreiben?"
        )

        if not answer:
            return

        saved_count = 0

        try:
            for path, rotation in changed_images:
                image = Image.open(path)
                rotated = image.rotate(rotation, expand=True)

                save_path = path
                rotated.save(save_path)

                self.rotation_map[path] = 0
                saved_count += 1

            self.update_image_preview()
            messagebox.showinfo("Speichern", f"{saved_count} Bilder gespeichert.")

        except Exception as e:
            messagebox.showerror("Fehler", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = VOBildTool(root)
    root.mainloop()