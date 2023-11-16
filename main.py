import json
from difflib import get_close_matches
import tkinter as tk

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.4)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base['questions']:
        if q['question'] == question:
            return q['answer']


def send_message():
    user_input = user_entry.get()
    chat_box.insert(tk.END, f"You: {user_input}\n")
    user_entry.delete(0, tk.END)

    if user_input.lower() == 'quit':
        quit()

    best_match = find_best_match(user_input, [q['question'] for q in knowledge_base['questions']])

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        chat_box.insert(tk.END, f"Clara: {answer}\n")
    else:
        new_answer = user_entry.get().strip()  # Get the new answer from user

        if new_answer.lower() == 'skip' or new_answer == '':
            chat_box.insert(tk.END, "Clara \n")

        if new_answer != 'skip':
            knowledge_base['questions'].append({'question': user_input, "answer": new_answer})
            save_knowledge_base('knowledge_base.json', knowledge_base)
            chat_box.insert(tk.END, 'Clara: Thanks for teaching me the answer!\n')

        # Clear the flag variable
        new_answer = None
def chat_bot():
    global knowledge_base
    knowledge_base = load_knowledge_base('knowledge_base.json')

    window = tk.Tk()
    window.title('ChatBot')

    chat_frame = tk.Frame(window)
    chat_frame.pack(pady=10)

    global chat_box
    chat_box = tk.Text(chat_frame, width=50, height=10)
    chat_box.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(chat_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_box.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=chat_box.yview)

    entry_frame = tk.Frame(window)
    entry_frame.pack(pady=10)

    global user_entry
    user_entry = tk.Entry(entry_frame, width=40)
    user_entry.pack(side=tk.LEFT, padx=5)

    send_button = tk.Button(entry_frame, text="Send", command=send_message)
    send_button.pack(side=tk.LEFT)

    window.mainloop()

if __name__ == '__main__':
    chat_bot()