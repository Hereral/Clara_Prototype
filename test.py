import json
import tkinter as tk
from tkinter import simpledialog
from difflib import get_close_matches


def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data: dict = json.load(file)
    except FileNotFoundError:
        data = {'question': []}
        save_knowledge_base(file_path, data)
    except json.decoder.JSONDecodeError:
        data = {'question': []}
        save_knowledge_base(file_path, data)

    if 'question' in data:
        if not isinstance(data['question'], list):
            data['question'] = []
        # Remove empty strings from the list of questions
        data['question'] = [q for q in data['question'] if q.get('question', '').strip()]
    else:
        data = {'question': []}
        save_knowledge_base(file_path, data)

    return data





def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def find_best_match(user_question: str, questions: list[str]) -> str | None:
    user_question = user_question.lower()
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base['question']:
        if q['question'].lower() == question:
            return q["answer"]


class ChatBotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Clara The Chatbot")

        self.knowledge_base = load_knowledge_base('knowledge_base.json')

        self.chat_history = tk.Text(master, state=tk.DISABLED, wrap=tk.WORD, width=40, height=10)
        self.chat_history.pack(padx=10, pady=10)

        self.user_input_entry = tk.Entry(master, width=40)
        self.user_input_entry.pack(pady=10)
        self.user_input_entry.bind('<Return>', self.handle_user_input)

        self.quit_button = tk.Button(master, text="Quit", command=self.master.destroy)
        self.quit_button.pack(pady=10)

    def handle_user_input(self, event=None):
        user_input = self.user_input_entry.get().strip()

        if not user_input:
            return  # Ignore empty input

        self.user_input_entry.delete(0, tk.END)

        if user_input.lower() == 'quit':
            self.master.destroy()

        if 'question' not in self.knowledge_base:
            self.knowledge_base['question'] = []

        questions = [q['question'].lower() for q in self.knowledge_base['question']]
        print(f"DEBUG: All Questions: {questions}")

        best_match = find_best_match(user_input.lower(), questions)
        print(f"DEBUG: Best Match: {best_match}")

        if best_match:
            answer = get_answer_for_question(best_match, self.knowledge_base)
            self.update_chat(f'You: {user_input}\nClara: {answer}\n')
        else:
            self.update_chat(f'You: {user_input}\nClara: I\'m not sure how to answer. Can you teach me?\n')
            existing_question = find_best_match(user_input.lower(), questions)
            print(f"DEBUG: Existing Question: {existing_question}")

            if existing_question and existing_question != user_input.lower():
                # If the similar question already exists (but not an exact match), get the answer from the knowledge base
                answer = get_answer_for_question(existing_question, self.knowledge_base)
                self.update_chat(f'Clara: I already know the answer: {answer}\n')
            else:
                new_answer = simpledialog.askstring('Teach Clara', 'Type the answer or click Cancel to skip: ')
                print(f"DEBUG: New Answer: {new_answer}")

                if new_answer is not None:
                    self.knowledge_base['question'].append({'question': user_input, "answer": new_answer})
                    save_knowledge_base('knowledge_base.json', self.knowledge_base)
                    self.update_chat('Chatbot: Thanks for teaching the answer!\n')

    def update_chat(self, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message)
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)


if __name__ == '__main__':
    root = tk.Tk()
    app = ChatBotApp(root)
    root.bind('<Return>', lambda event=None: app.handle_user_input(event))  # Bind Enter key to handle_user_input
    root.mainloop()

