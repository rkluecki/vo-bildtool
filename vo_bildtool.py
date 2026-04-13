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
        self.crop_map = {}

        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect_id = None
        self.crop_end_x = None
        self.crop_end_y = None

        self.display_image_x = 0
        self.display_image_y = 0
        self.display_image_width = 0
        self.display_image_height = 0
        self.original_image_width = 0
        self.original_image_height = 0

        self.allowed_extensions = (
            ".gif",
            ".jpg",
            ".jpeg",
            ".png",
            ".tif",
            ".tiff",
            ".bmp",
        )

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
            top_frame, text="Ordner öffnen", command=self.open_folder, width=20
        )
        self.btn_open_folder.pack(side=tk.LEFT)

        self.btn_next = tk.Button(
            top_frame, text="Nächstes →", command=self.next_image, width=15
        )
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.btn_jump_back = tk.Button(
            top_frame, text="<< 10", command=self.jump_back_10, width=8
        )
        self.btn_jump_back.pack(side=tk.LEFT, padx=5)

        self.btn_jump_forward = tk.Button(
            top_frame, text="10 >>", command=self.jump_forward_10, width=8
        )
        self.btn_jump_forward.pack(side=tk.LEFT, padx=5)

        self.btn_prev = tk.Button(
            top_frame, text="← Vorheriges", command=self.previous_image, width=15
        )
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_rotate_right = tk.Button(
            top_frame, text="Rechts ⟳", command=self.rotate_right, width=15
        )
        self.btn_rotate_right.pack(side=tk.LEFT, padx=5)

        self.btn_rotate_left = tk.Button(
            top_frame, text="Links ⟲", command=self.rotate_left, width=15
        )
        self.btn_rotate_left.pack(side=tk.LEFT, padx=5)

        self.btn_rotate_180 = tk.Button(
            top_frame, text="180°", command=self.rotate_180, width=10
        )
        self.btn_rotate_180.pack(side=tk.LEFT, padx=5)

        self.btn_reset = tk.Button(
            top_frame, text="Reset", command=self.reset_rotation, width=10
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        self.btn_save = tk.Button(
            top_frame, text="Speichern", command=self.save_images, width=12
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.lbl_goto = tk.Label(top_frame, text="Gehe zu Bild:")
        self.lbl_goto.pack(side=tk.LEFT, padx=(15, 5))

        vcmd = (self.root.register(self.validate_number), "%P")

        self.entry_goto = tk.Entry(
            top_frame, width=8, validate="key", validatecommand=vcmd
        )
        self.entry_goto.pack(side=tk.LEFT, padx=5)

        self.btn_goto = tk.Button(
            top_frame, text="Gehe zu", command=self.go_to_image, width=10
        )
        self.btn_goto.pack(side=tk.LEFT, padx=5)

        self.entry_goto.bind("<Return>", self.go_to_image)

        self.lbl_folder = tk.Label(top_frame, text="Kein Ordner gewählt", anchor="w")
        self.lbl_folder.pack(side=tk.LEFT, padx=10)

        info_frame = tk.Frame(self.root)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))

        self.lbl_file = tk.Label(info_frame, text="Keine Datei geladen", anchor="w")
        self.lbl_file.pack(side=tk.TOP, fill=tk.X)

        self.lbl_count = tk.Label(info_frame, text="Bild 0 von 0", anchor="w")
        self.lbl_count.pack(side=tk.TOP, fill=tk.X)

        self.image_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        #  self.canvas = tk.Canvas(self.image_frame, bg="black")
        self.canvas = tk.Canvas(self.image_frame, bg="#777777")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.bind("<Configure>", self.on_window_resize)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

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

                if os.path.isfile(full_path) and file_name.lower().endswith(
                    self.allowed_extensions
                ):
                    files.append(full_path)

            files.sort()

            self.image_files = files
            self.current_index = 0

            if not self.image_files:
                self.current_pil_image = None
                self.current_tk_image = None
                self.image_label.config(
                    image="", text="Keine Bilddateien im Ordner gefunden"
                )
                self.lbl_file.config(text="Keine Datei geladen")
                self.lbl_count.config(text="Bild 0 von 0")
                messagebox.showinfo(
                    "Hinweis",
                    "Im gewählten Ordner wurden keine unterstützten Bilddateien gefunden.",
                )
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

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 50 or canvas_height < 50:
            self.root.after(100, self.update_image_preview)
            return

        path = self.image_files[self.current_index]
        rotation = self.rotation_map.get(path, 0)

        image_copy = self.current_pil_image.copy().rotate(rotation, expand=True)

        self.original_image_width = image_copy.width
        self.original_image_height = image_copy.height

        image_copy.thumbnail((canvas_width - 20, canvas_height - 20))

        self.display_image_width = image_copy.width
        self.display_image_height = image_copy.height

        self.current_tk_image = ImageTk.PhotoImage(image_copy)

        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        image_x = (canvas_width - self.display_image_width) // 2
        image_y = (canvas_height - self.display_image_height) // 2

        self.display_image_x = image_x
        self.display_image_y = image_y

        self.canvas.create_image(
            image_x, image_y, image=self.current_tk_image, anchor="nw"
        )

        path = self.image_files[self.current_index]
        saved_crop = self.crop_map.get(path)

        if saved_crop:
            x1, y1, x2, y2 = saved_crop
            self.crop_rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="red", width=2
            )
        else:
            self.crop_rect_id = None

        path = self.image_files[self.current_index]
        rotation = self.rotation_map.get(path, 0)
        self.lbl_count.config(
            text=f"Bild {self.current_index + 1} von {len(self.image_files)}   |   Drehung: {rotation}°"
        )

    def get_crop_box_for_current_image(self):
        path = self.image_files[self.current_index]
        saved_crop = self.crop_map.get(path)

        if not saved_crop:
            return None

        x1, y1, x2, y2 = saved_crop

        x_left = min(x1, x2)
        y_top = min(y1, y2)
        x_right = max(x1, x2)
        y_bottom = max(y1, y2)

        image_left = self.display_image_x
        image_top = self.display_image_y
        image_right = self.display_image_x + self.display_image_width
        image_bottom = self.display_image_y + self.display_image_height

        x_left = max(x_left, image_left)
        y_top = max(y_top, image_top)
        x_right = min(x_right, image_right)
        y_bottom = min(y_bottom, image_bottom)

        if x_right <= x_left or y_bottom <= y_top:
            return None

        rel_x1 = x_left - self.display_image_x
        rel_y1 = y_top - self.display_image_y
        rel_x2 = x_right - self.display_image_x
        rel_y2 = y_bottom - self.display_image_y

        scale_x = self.original_image_width / self.display_image_width
        scale_y = self.original_image_height / self.display_image_height

        img_x1 = int(rel_x1 * scale_x)
        img_y1 = int(rel_y1 * scale_y)
        img_x2 = int(rel_x2 * scale_x)
        img_y2 = int(rel_y2 * scale_y)

        img_x1 = max(0, min(img_x1, self.original_image_width))
        img_y1 = max(0, min(img_y1, self.original_image_height))
        img_x2 = max(0, min(img_x2, self.original_image_width))
        img_y2 = max(0, min(img_y2, self.original_image_height))

        if img_x2 <= img_x1 or img_y2 <= img_y1:
            return None

        return (img_x1, img_y1, img_x2, img_y2)

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

    def jump_forward_10(self):
        if not self.image_files:
            return

        self.current_index = min(self.current_index + 10, len(self.image_files) - 1)
        self.show_current_image()

    def jump_back_10(self):
        if not self.image_files:
            return

        self.current_index = max(self.current_index - 10, 0)
        self.show_current_image()

    def go_to_image(self, event=None):
        if not self.image_files:
            return

        value = self.entry_goto.get().strip()

        if not value.isdigit():
            messagebox.showwarning(
                "Ungültige Eingabe", "Bitte eine Bildnummer eingeben."
            )
            return

        image_number = int(value)

        if image_number < 1 or image_number > len(self.image_files):
            messagebox.showwarning(
                "Ungültige Bildnummer",
                f"Bitte eine Zahl zwischen 1 und {len(self.image_files)} eingeben.",
            )
            return

        self.current_index = image_number - 1
        self.show_current_image()

    def validate_number(self, value):
        return value.isdigit() or value == ""

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
        changed_images = []

        for path in self.image_files:
            rotation = self.rotation_map.get(path, 0)
            crop = self.crop_map.get(path)

            if rotation != 0 or crop:
                changed_images.append(path)

        if not changed_images:
            messagebox.showinfo("Speichern", "Keine geänderten Bilder vorhanden.")
            return

        answer = messagebox.askyesno(
            "Bestätigung", f"{len(changed_images)} Bilder wirklich überschreiben?"
        )

        if not answer:
            return

        saved_count = 0

        try:
            for path in self.image_files:
                rotation = self.rotation_map.get(path, 0)
                crop = self.crop_map.get(path)

                if rotation == 0 and not crop:
                    continue

                image = Image.open(path)
                result = image.copy()

                if rotation != 0:
                    result = result.rotate(rotation, expand=True)

                if crop:
                    x1, y1, x2, y2 = crop

                    left = min(x1, x2)
                    top = min(y1, y2)
                    right = max(x1, x2)
                    bottom = max(y1, y2)

                    if right > left and bottom > top:
                        result = result.crop((left, top, right, bottom))

                result.save(path)

                self.rotation_map[path] = 0
                if path in self.crop_map:
                    del self.crop_map[path]

                saved_count += 1

            self.show_current_image()
            messagebox.showinfo("Speichern", f"{saved_count} Bilder gespeichert.")

        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def on_mouse_down(self, event):
        if not self.image_files:
            return

        path = self.image_files[self.current_index]

        if self.crop_rect_id is not None:
            self.canvas.delete(self.crop_rect_id)
            self.crop_rect_id = None

        if path in self.crop_map:
            del self.crop_map[path]

        self.crop_end_x = None
        self.crop_end_y = None

        self.crop_start_x = event.x
        self.crop_start_y = event.y

        print(f"Neuer Start: {event.x}, {event.y}")

    def on_mouse_drag(self, event):
        if self.crop_start_x is None or self.crop_start_y is None:
            return

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        if self.crop_rect_id is not None:
            self.canvas.delete(self.crop_rect_id)

        self.crop_rect_id = self.canvas.create_rectangle(
            self.crop_start_x,
            self.crop_start_y,
            self.crop_end_x,
            self.crop_end_y,
            outline="red",
            width=2,
        )

    def on_mouse_up(self, event):
        if self.crop_start_x is None or self.crop_start_y is None:
            return

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        path = self.image_files[self.current_index]

        x1 = self.crop_start_x
        y1 = self.crop_start_y
        x2 = self.crop_end_x
        y2 = self.crop_end_y

        x_left = min(x1, x2)
        y_top = min(y1, y2)
        x_right = max(x1, x2)
        y_bottom = max(y1, y2)

        image_left = self.display_image_x
        image_top = self.display_image_y
        image_right = self.display_image_x + self.display_image_width
        image_bottom = self.display_image_y + self.display_image_height

        x_left = max(x_left, image_left)
        y_top = max(y_top, image_top)
        x_right = min(x_right, image_right)
        y_bottom = min(y_bottom, image_bottom)

        if x_right <= x_left or y_bottom <= y_top:
            print("Kein gültiger Zuschneidebereich im Bild.")
            return

        rel_x1 = x_left - self.display_image_x
        rel_y1 = y_top - self.display_image_y
        rel_x2 = x_right - self.display_image_x
        rel_y2 = y_bottom - self.display_image_y

        scale_x = self.original_image_width / self.display_image_width
        scale_y = self.original_image_height / self.display_image_height

        img_x1 = int(rel_x1 * scale_x)
        img_y1 = int(rel_y1 * scale_y)
        img_x2 = int(rel_x2 * scale_x)
        img_y2 = int(rel_y2 * scale_y)

        img_x1 = max(0, min(img_x1, self.original_image_width))
        img_y1 = max(0, min(img_y1, self.original_image_height))
        img_x2 = max(0, min(img_x2, self.original_image_width))
        img_y2 = max(0, min(img_y2, self.original_image_height))

        self.crop_map[path] = (img_x1, img_y1, img_x2, img_y2)

        print(
            f"Crop-Bildkoordinaten gespeichert: "
            f"({img_x1}, {img_y1}) -> ({img_x2}, {img_y2})"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = VOBildTool(root)
    root.mainloop()
