import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import time
import pyperclip
import requests
from bs4 import BeautifulSoup

class SpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Reading App")

        self.text_entry = tk.Text(root, wrap="word", width=50, height=10, font=("Helvetica", 50))
        self.text_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

        self.size_label = ttk.Label(root, text="Text Size:")
        self.size_label.grid(row=1, column=0, padx=10, pady=10)

        self.size_label = ttk.Label(root, text="Speed:")
        self.size_label.grid(row=1, column=2, padx=10, pady=10)

        self.size_entry = ttk.Entry(root, width=10)
        self.size_entry.insert(0, "50")  # Default size
        self.size_entry.grid(row=1, column=1, padx=10, pady=10)

        self.speed = ttk.Entry(root, width=10)
        self.speed.insert(0, "400")  # Default speed
        self.speed.grid(row=1, column=3, padx=10, pady=10)

        self.load_file_button = ttk.Button(root, text="Load Text from File", command=self.load_text_from_file)
        self.load_file_button.grid(row=2, column=0, padx=10, pady=10)

        self.load_clipboard_button = ttk.Button(root, text="Load Text from Clipboard", command=self.load_text_from_clipboard)
        self.load_clipboard_button.grid(row=2, column=1, padx=10, pady=10)

        #self.start_button = ttk.Button(root, text="Start Reading", command=self.start_reading)
        #self.start_button.grid(row=3, column=1, padx=10, pady=10)

        self.clean_button = ttk.Button(root, text="Clean Text from Website", command=self.clean_text_from_website)
        self.clean_button.grid(row=2, column=2, padx=10, pady=10)

        self.pause_button = ttk.Button(root, text="Pause/Resume", command=self.pause_reading)
        self.pause_button.grid(row=3, column=0, padx=10, pady=10)

        self.paused = True
        self.words = []
        self.current_word_index = 0
        self.paused_words = []

    def clean_text_from_website(self):
        url = simpledialog.askstring("Website URL", "Enter the URL of the website:")
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Process text content
                text_parts = []
                for element in soup.find_all(['p']):
                    if element.name == 'a':
                        # Process link text
                        text_parts.append(f"[{element.get_text()}]")
                    else:
                        # Process other elements and text
                        text_parts.append(element.get_text())

                text = ' '.join(text_parts)

                # Update the text entry
                self.text_entry.delete(1.0, tk.END)
                self.text_entry.insert(tk.END, text)
                self.words = text.split()
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

    def load_text_from_file(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                text = file.read()
            self.text_entry.delete(1.0, tk.END)
            self.text_entry.insert(tk.END, text)
            self.words = text.split()

    def load_text_from_clipboard(self):
        clipboard_text = pyperclip.paste()
        if clipboard_text.strip():
            self.text_entry.delete(1.0, tk.END)
            self.text_entry.insert(tk.END, clipboard_text)
            self.words = clipboard_text.split()

    def start_reading(self):
        if not self.paused:
            text = self.text_entry.get("1.0", tk.END)
            size = int(self.size_entry.get())
            speed = float(self.speed.get())

            self.text_entry.config(font=("Helvetica", size))

            if text and speed > 0:
                words = text.split()
                delay = 60 / speed

                for i in range(self.current_word_index, len(self.words)):
                    if self.paused:
                       break
                    self.text_entry.delete(1.0, tk.END)
                    self.text_entry.insert(tk.END, self.words[i])
                    self.text_entry.tag_configure("center", justify="center")
                    self.text_entry.tag_add("center", 1.0, tk.END)
                    self.root.update()
                    time.sleep(delay)
                    self.current_word_index = i + 1
            if self.current_word_index == len(self.words):
                self.current_word_index = 0
            self.show_last_words()

    def pause_reading(self):
        self.paused = not self.paused
        self.start_reading()
        if self.paused:
        #   # Capture the last 15 words before pausing
            self.paused_words = self.words[max(0, self.current_word_index - 30):self.current_word_index]

    def show_last_words(self):
        if self.paused and self.paused_words:
            # Create a pop-up window to display the last 30 words before pausing
            popup = tk.Toplevel(self.root)
            popup.title("Last 30 Words Before Pause")

            text = " ".join(self.paused_words)
            label = tk.Text(popup, width=50, height=10)
            label.insert(tk.END, text)
            label.pack(padx=100, pady=100)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReaderApp(root)
    root.mainloop()
