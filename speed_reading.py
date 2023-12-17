import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import time
import pyperclip
import requests
from bs4 import BeautifulSoup
from functools import partial

class SpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Reading App")

        self.text_entry = tk.Text(root, wrap="word", width=50, height=10, font=("Helvetica", 50))
        self.text_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

        self.size_label = ttk.Label(root, text="Text Size:")
        self.size_label.grid(row=1, column=0, padx=0, pady=0)

        self.size_label = ttk.Label(root, text="Speed:")
        self.size_label.grid(row=1, column=1, padx=0, pady=0)

        self.size_entry = ttk.Entry(root, width=10)
        self.size_entry.insert(0, "50")  # Default size
        self.size_entry.grid(row=2, column=0, padx=0, pady=0)

        self.speed = ttk.Entry(root, width=10)
        self.speed.insert(0, "450")  # Default speed
        self.speed.grid(row=2, column=1, padx=0, pady=0)

        self.load_file_button = ttk.Button(root, text="Load Text from File", command=self.load_text_from_file)
        self.load_file_button.grid(row=3, column=0, padx=10, pady=10)

        self.load_clipboard_button = ttk.Button(root, text="Load Text from Clipboard", command=self.load_text_from_clipboard)
        self.load_clipboard_button.grid(row=4, column=0, padx=10, pady=10)

        self.clean_button = ttk.Button(root, text="Clean Text from Website", command=self.clean_text_from_website)
        self.clean_button.grid(row=5, column=0, padx=10, pady=10)

        self.pause_button = ttk.Button(root, text="Pause/Resume", command=self.pause_reading)
        self.pause_button.grid(row=3, column=1, padx=10, pady=10)

        self.label = tk.Text(self.root, width=50, height=10)

        self.backwards_button = ttk.Button(root, text="<<", command=self.set_words_before)
        self.backwards_button.grid(row=4, column=1, padx=0, pady=10)

        self.forwards_button = ttk.Button(root, text=">>", command=self.set_words_forward)
        self.forwards_button.grid(row=5, column=1, padx=0, pady=10)

        self.label.grid(row=1, column=2, padx=10, pady=10, rowspan=5)

        self.paused = True
        self.words = []
        self.current_word_index = 0
        self.paused_words = []
        self.cache_index = 0
        self.PAUSE_WORD_LEN = 20

    def clean_words(self):
        self.paused = True
        self.words = []
        self.current_word_index = 0
        self.cache_index = 0
        self.paused_words = []

    def clean_text_from_website(self):
        self.clean_words()
        url = simpledialog.askstring("Website URL", "Enter the URL of the website:")
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Process text content around links
                text_parts = []
                for element in soup.find_all(['p']):
                    if element.name == 'a':
                        # Process link text, e.g., append the link text in square brackets
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
        self.clean_words()
        file_path = tk.filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                text = file.read()
            self.text_entry.delete(1.0, tk.END)
            self.text_entry.insert(tk.END, text)
            self.words = text.split()

    def load_text_from_clipboard(self):
        self.clean_words()
        clipboard_text = pyperclip.paste()
        if clipboard_text.strip():
            self.text_entry.delete(1.0, tk.END)
            self.text_entry.insert(tk.END, clipboard_text)
            self.words = clipboard_text.split()

    def start_reading(self):
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
                len_word = len(self.words[i]) 
                if len_word > 8:
                    time.sleep((len_word/6)*delay)
                else:
                    time.sleep(delay)
                self.current_word_index = i + 1
        # If the loop is breaked:
        if self.current_word_index == len(self.words):
            self.current_word_index = 0
        self.show_last_words()

    def pause_reading(self):
        self.paused = not self.paused
        self.clear_last_words()
        if not self.paused:
            self.start_reading()
        else:
            # Capture the last self.PAUSE_WORD_LEN words before pausing
            self.set_paused_words(self.current_word_index - self.PAUSE_WORD_LEN, self.current_word_index) #TODO again done in set_words_before()
            self.cache_index = self.current_word_index - self.PAUSE_WORD_LEN
    
    def clear_last_words(self):
        self.paused_words = []
        self.set_side_text()

    def set_paused_words(self, num, current_index):
        # TODO also into clipboard for easier note taking
        print(f"Num is {num}")
        print(f"Current index is {current_index}")
        start = max(0, num)
        end = max(0, current_index)
        self.paused_words = self.words[start:end]
        # find beginning and end of a sentence
        end_of_sentence = "."
        while start > 0 and not end_of_sentence in self.words[start]:
            start -= 1
            if not end_of_sentence in self.words[start]:
                self.paused_words.insert(0,self.words[start])
        while end < len(self.words):
            if not end_of_sentence in self.words[end]:
                self.paused_words.append(self.words[end])
            else:
                # the word with the dot (.) should also be added
                self.paused_words.append(self.words[end])
                break
            end += 1
        print(self.paused_words)
    
    def set_side_text(self):
        text = " ".join(self.paused_words)
        try:
            self.label.delete(1.0, tk.END)
        except Exception as e:
            print(e)
        self.label.insert(tk.END, text)
    
    def set_words_before(self):
        self.set_paused_words(self.cache_index - self.PAUSE_WORD_LEN, self.cache_index)
        self.cache_index -= self.PAUSE_WORD_LEN
        self.set_side_text()

    def set_words_forward(self):
        self.set_paused_words(self.cache_index, self.cache_index + self.PAUSE_WORD_LEN)
        self.cache_index += self.PAUSE_WORD_LEN
        self.set_side_text()

    def show_last_words(self):
        if self.paused and self.paused_words:
            #self.cache_index = self.current_word_index
            self.set_side_text()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReaderApp(root)
    root.mainloop()
