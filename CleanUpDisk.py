import os
import shutil
import tempfile
from pathlib import Path
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import threading

def get_resource_path(rel_path):
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = Path(__file__).resolve().parent
    else:
        base = Path(base)
    return base / rel_path

def clean_temp_folder(path, log_widget, progress, step):
    deleted_files = 0
    deleted_folders = 0
    skipped = 0

    if not os.path.exists(path):
        log_widget.insert(tk.END, f"[!] Path not found: {path}\n")
        progress.step(step)
        progress.update()
        return (0, 0, 0)

    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                deleted_files += 1
            except Exception:
                skipped += 1

        for folder in dirs:
            folder_path = os.path.join(root, folder)
            try:
                shutil.rmtree(folder_path, ignore_errors=True)
                deleted_folders += 1
            except Exception:
                skipped += 1

    progress.step(step)
    progress.update()
    return deleted_files, deleted_folders, skipped

def run_cleanup(log_widget, progress, paths_to_clean):
    def task():
        log_widget.delete(1.0, tk.END)
        log_widget.insert(tk.END, "=== Windows 11 Temp Cleaner ===\n\n")

        all_paths = list(paths_to_clean)

        total_files = total_folders = total_skipped = 0
        step = 100 / max(len(all_paths), 1)

        for path in all_paths:
            log_widget.insert(tk.END, f"Cleaning: {path}\n")
            f, d, s = clean_temp_folder(path, log_widget, progress, step)
            log_widget.insert(tk.END, f" -> Deleted {f} files, {d} folders, skipped {s}\n\n")
            total_files += f
            total_folders += d
            total_skipped += s

        summary = (
            f"=== Cleanup Summary ===\n"
            f" Total deleted files   : {total_files}\n"
            f" Total deleted folders : {total_folders}\n"
            f" Skipped (locked/in use): {total_skipped}\n\n"
            "✅ Cleanup completed. Locked files were skipped, but cleanup continued.\n"
        )
        log_widget.insert(tk.END, summary)
        messagebox.showinfo("Cleanup Completed", summary)

    threading.Thread(target=task, daemon=True).start()

def create_app():
    root = tk.Tk()
    root.title("Windows 11 Temp Cleaner")
    root.configure(bg="#f4f7fb")

    if os.name == "nt":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.example.cleanupdisk")
        except Exception:
            pass

    # Use a modern ttk theme and custom styles
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Colors and fonts
    primary = "#0b69ff"
    accent = "#17a2b8"
    success = "#28a745"
    danger = "#dc3545"
    warning = "#ffc107"
    secondary = "#6c757d"
    purple = "#6f42c1"
    card_bg = "#ffffff"
    root_font = ("Segoe UI", 10)

    style.configure("TFrame", background=root["bg"])
    style.configure("Card.TFrame", background=card_bg, relief="flat")
    style.configure("Header.TLabel", background=root["bg"], font=("Segoe UI", 18, "bold"), foreground="#222")
    style.configure("Sub.TLabel", background=card_bg, font=root_font, foreground="#444")

    # Generic button styles (specific ones below)
    style.configure("Primary.TButton", background=primary, foreground="white", font=root_font, padding=8)
    style.map("Primary.TButton", background=[("active", "#095ad6")])

    style.configure("Accent.TButton", background=accent, foreground="white", font=root_font, padding=6)
    style.map("Accent.TButton", background=[("active", "#138f9e")])

    style.configure("Success.TButton", background=success, foreground="white", font=root_font, padding=8)
    style.map("Success.TButton", background=[("active", "#208838")])

    style.configure("Danger.TButton", background=danger, foreground="white", font=root_font, padding=6)
    style.map("Danger.TButton", background=[("active", "#b21f2d")])

    # Additional colored button styles
    style.configure("AddFolder.TButton", background=purple, foreground="white", font=root_font, padding=6)
    style.map("AddFolder.TButton", background=[("active", "#5930a6")])

    style.configure("AddTemp.TButton", background=success, foreground="white", font=root_font, padding=6)
    style.map("AddTemp.TButton", background=[("active", "#208838")])

    style.configure("Warning.TButton", background=warning, foreground="black", font=root_font, padding=6)
    style.map("Warning.TButton", background=[("active", "#e0a800")])

    style.configure("Secondary.TButton", background=secondary, foreground="white", font=root_font, padding=6)
    style.map("Secondary.TButton", background=[("active", "#545b62")])

    # Load icon
    ico_path = get_resource_path(Path("Icons") / "app.ico")
    png_path = get_resource_path(Path("Icons") / "app.png")
    try:
        if ico_path.exists():
            root.iconbitmap(str(ico_path))
            if os.name == "nt":
                try:
                    root.update_idletasks()
                    hwnd = root.winfo_id()
                    LR_LOADFROMFILE = 0x00000010
                    IMAGE_ICON = 1
                    WM_SETICON = 0x0080
                    ICON_SMALL = 0
                    ICON_BIG = 1
                    hicon = ctypes.windll.user32.LoadImageW(0, str(ico_path), IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
                    if hicon:
                        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
                except Exception:
                    pass
        elif png_path.exists():
            img = tk.PhotoImage(file=str(png_path))
            root.iconphoto(True, img)
            root._icon_img = img
    except Exception as e:
        print("[!] Failed to set icon:", e)

    header_frame = ttk.Frame(root, style="TFrame")
    header_frame.pack(fill="x", pady=(18, 6))
    ttk.Label(header_frame, text="🧹 Windows 11 Temp Cleaner", style="Header.TLabel").pack(padx=20, anchor="center")

    # Main card
    card = ttk.Frame(root, style="Card.TFrame", padding=(16, 12))
    card.pack(fill="both", expand=True, padx=18, pady=10)

    paths_to_clean = []

    # Frame for folder selection
    folder_frame = ttk.Frame(card, style="Card.TFrame")
    folder_frame.pack(fill="x", pady=(8, 12))
    folder_frame.columnconfigure(0, weight=1)

    folder_listbox = tk.Listbox(folder_frame, height=6, selectmode=tk.SINGLE, bd=0, relief="flat",
                                font=root_font, highlightthickness=1, highlightbackground="#e3e6ea")
    folder_listbox.grid(row=1, column=0, columnspan=6, padx=5, pady=6, sticky="ew")

    log_widget = scrolledtext.ScrolledText(card, height=18, wrap=tk.WORD, font=root_font,
                                          bg="#ffffff", fg="#222", bd=0, relief="flat", highlightthickness=1,
                                          highlightbackground="#e3e6ea")
    log_widget.pack(pady=8, padx=2, fill="both", expand=True)

    progress = ttk.Progressbar(card, mode="determinate")
    progress.pack(pady=8, padx=4, fill="x")

    def add_folder(name, path):
        if path not in paths_to_clean:
            paths_to_clean.append(path)
            folder_listbox.insert(tk.END, f"{name}: {path}")
            log_widget.insert(tk.END, f"[+] Added {name}: {path}\n")

    def add_custom_folder():
        folder = filedialog.askdirectory(title="Select folder to clean")
        if folder:
            add_folder("Custom", folder)

    def remove_selected_folder():
        selection = folder_listbox.curselection()
        if selection:
            idx = selection[0]
            folder_listbox.delete(idx)
            removed_path = paths_to_clean.pop(idx)
            log_widget.insert(tk.END, f"[-] Removed folder: {removed_path}\n")

    def add_temp_folders():
        user_temp = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp"
        system_temp = Path("C:/Windows/Temp")
        python_temp = Path(tempfile.gettempdir())
        add_folder("User Temp", str(user_temp))
        add_folder("Windows Temp", str(system_temp))
        add_folder("Python Temp", str(python_temp))

    # Buttons for common folders (reordered and colored)
    btn_frame = ttk.Frame(folder_frame, style="Card.TFrame")
    btn_frame.grid(row=0, column=0, columnspan=6, sticky="w", pady=(4, 6))

    # Start with Add Folder then Add Temp, then the rest
    ttk.Button(btn_frame, text="Add Folder...", command=add_custom_folder, style="AddFolder.TButton").grid(row=0, column=0, padx=6, pady=4)
    ttk.Button(btn_frame, text="Add Temp Folders", command=add_temp_folders, style="AddTemp.TButton").grid(row=0, column=1, padx=6, pady=4)
    ttk.Button(btn_frame, text="Recent", command=lambda: add_folder("Recent", str(Path.home() / "AppData/Roaming/Microsoft/Windows/Recent")), style="Primary.TButton").grid(row=0, column=2, padx=6, pady=4)
    ttk.Button(btn_frame, text="Documents", command=lambda: add_folder("Documents", str(Path.home() / "Documents")), style="Accent.TButton").grid(row=0, column=3, padx=6, pady=4)
    ttk.Button(btn_frame, text="Downloads", command=lambda: add_folder("Downloads", str(Path.home() / "Downloads")), style="Warning.TButton").grid(row=0, column=4, padx=6, pady=4)
    ttk.Button(btn_frame, text="Desktop", command=lambda: add_folder("Desktop", str(Path.home() / "Desktop")), style="Secondary.TButton").grid(row=0, column=5, padx=6, pady=4)

    ttk.Button(folder_frame, text="Remove Selected", command=remove_selected_folder, style="Danger.TButton").grid(row=2, column=0, columnspan=6, pady=(8, 2))

    # Bottom buttons
    button_frame = ttk.Frame(card, style="Card.TFrame")
    button_frame.pack(pady=10)

    clean_button = ttk.Button(
        button_frame, text="Start Cleanup", style="Success.TButton",
        command=lambda: run_cleanup(log_widget, progress, paths_to_clean)
    )
    clean_button.grid(row=0, column=0, padx=16)

    exit_button = ttk.Button(
        button_frame, text="Exit", style="Danger.TButton",
        command=root.destroy
    )
    exit_button.grid(row=0, column=1, padx=16)

    # subtle footer
    footer = ttk.Frame(root, style="TFrame")
    footer.pack(fill="x", pady=(6, 12))
    ttk.Label(footer, text="Tip: Add common temp folders then press Start Cleanup", style="Sub.TLabel").pack(anchor="center")

    # Let Tk compute a size that fits content, then center on screen
    root.update_idletasks()
    req_w = root.winfo_reqwidth() + 40
    req_h = root.winfo_reqheight() + 40
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w // 2) - (req_w // 2)
    y = (screen_h // 2) - (req_h // 2)
    root.geometry(f"{req_w}x{req_h}+{x}+{y}")
    root.minsize(500, 360)  # modest minimum to avoid being too small

    root.mainloop()

if __name__ == "__main__":
    create_app()
