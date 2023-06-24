import sqlite3
import tkinter as tk
from tkinter import messagebox


def create_connection():
    conn = sqlite3.connect('helpdesk.db')
    return conn

def check_password(conn, user, password):
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (user,))
    result = cursor.fetchone()
    if result and result[0] == password:
        return True
    else:
        return False

def create_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS tickets
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    issue TEXT NOT NULL,
                    solution TEXT);''')
    conn.commit()

def create_knowledge_base(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS knowledge_base
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue TEXT NOT NULL,
                    solution TEXT NOT NULL);''')
    conn.commit()

def insert_knowledge(conn, issue, solution):
    conn.execute("INSERT INTO knowledge_base (issue,solution) VALUES (?, ?)", (issue, solution))
    conn.commit()

def search_knowledge(conn, issue):
    cursor = conn.cursor()
    cursor.execute("SELECT solution FROM knowledge_base WHERE issue = ?", (issue,))
    return cursor.fetchone()

def insert_ticket(conn, user, issue):
    conn.execute("INSERT INTO tickets (user,issue) VALUES (?, ?)", (user, issue))
    conn.commit()

def solve_ticket(conn, ticket_id, solution):
    conn.execute("UPDATE tickets SET solution = ? WHERE id = ?", (solution, ticket_id))
    conn.commit()

def get_all_tickets(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    return cursor.fetchall()

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(sticky="nsew")
        self.conn = create_connection()
        self.create_widgets()
        create_table(self.conn)
        create_knowledge_base(self.conn)

    def create_widgets(self):
        self.user_entry = tk.Entry(self)
        self.user_entry.grid(row=0, column=1, sticky="nsew")
        tk.Label(self, text="User").grid(row=0)

        self.issue_entry = tk.Entry(self)
        self.issue_entry.grid(row=1, column=1, sticky="nsew")
        tk.Label(self, text="Issue").grid(row=1)

        self.submit_button = tk.Button(self, text="SUBMIT", fg="red", command=self.submit_issue)
        self.submit_button.grid(row=2, column=1, sticky="nsew")

        self.solve_button = tk.Button(self, text="SOLVE", fg="green", command=self.solve_issue)
        self.solve_button.grid(row=3, column=1, sticky="nsew")

        self.solution_entry = tk.Entry(self)
        self.solution_entry.grid(row=3, column=2, sticky="nsew")

        self.search_button = tk.Button(self, text="SEARCH", fg="blue", command=self.search_knowledge)
        self.search_button.grid(row=4, column=2, sticky="nsew")

        self.search_result = tk.Label(self, text="")
        self.search_result.grid(row=5, column=1, columnspan=2, sticky="nsew")

        self.ticket_history = tk.Listbox(self)
        self.ticket_history.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.refresh_history()

        self.solution_entry = tk.Entry(self)
        self.solution_entry.grid(row=3, column=2, sticky="nsew")

        self.add_button = tk.Button(self, text="ADD TO KB", fg="purple", command=self.add_solution)
        self.add_button.grid(row=4, column=2, sticky="nsew")

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, sticky="nsew")
        tk.Label(self, text="Username").grid(row=0)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, sticky="nsew")
        tk.Label(self, text="Password").grid(row=1)

    def add_solution(self):
        issue = self.issue_entry.get()
        solution = self.solution_entry.get()
        if issue and solution:
            insert_knowledge(self.conn, issue, solution)
            messagebox.showinfo("Success", "Solution added to the knowledge base!")
        else:
            messagebox.showerror("Error", "Issue and Solution fields cannot be empty")

    def refresh_history(self):
        self.ticket_history.delete(0, tk.END)
        tickets = get_all_tickets(self.conn)
        for ticket in tickets:
            self.ticket_history.insert(tk.END, f"Ticket ID: {ticket[0]}, User: {ticket[1]}, Issue: {ticket[2]}, Solution: {ticket[3]}")

    def submit_issue(self):
        user = self.username_entry.get()
        password = self.password_entry.get()
        issue = self.issue_entry.get()
        if user and password and issue and check_password(self.conn, user, password):
            insert_ticket(self.conn, user, issue)
            self.refresh_history()
            messagebox.showinfo("Success", "Ticket submitted successfully!")
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def solve_issue(self):
        solution = self.solution_entry.get()
        if solution:
            tickets = get_all_tickets(self.conn)
            if tickets:
                solve_ticket(self.conn, tickets[-1][0], solution)
                self.refresh_history()
                messagebox.showinfo("Success", "Ticket solved successfully!")
            else:
                messagebox.showerror("Error", "No tickets to solve")
        else:
            messagebox.showerror("Error", "Solution field cannot be empty")

    def search_knowledge(self):
        issue = self.issue_entry.get()
        if issue:
            result = search_knowledge(self.conn, issue)
            if result:
                self.search_result['text'] = "Found solution: " + result[0]
            else:
                self.search_result['text'] = "No solution found in the knowledge base"
        else:
            messagebox.showerror("Error", "Issue field cannot be empty")

root = tk.Tk()
root.title("Helpdesk System")
app = Application(master=root)
app.mainloop()
conn.execute("UPDATE tickets SET solution = ? WHERE id = ?", ("solution", 1))
conn.commit()
