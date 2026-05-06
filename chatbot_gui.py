# ------------------------------------------------------------
# INSTALL THESE LIBRARIES FIRST:
# pip install pandas rapidfuzz
#
# tkinter usually comes built into Python, so in most cases
# you do not need to install it separately.
# ------------------------------------------------------------


# ------------------------------------------------------------
# SECTION 1: IMPORT LIBRARIES
# In this section, we import all the tools needed for the chatbot.
# We need:
# 1. tkinter to create the desktop chat window
# 2. pandas to read the CSV file
# 3. rapidfuzz to compare user questions with stored FAQ questions
# ------------------------------------------------------------

import tkinter as tk  # Lets us build the main graphical user interface window and widgets.
from tkinter import scrolledtext  # Gives us a text area with a built-in scrollbar for chat messages.
from tkinter import messagebox  # Lets us show popup error messages if something goes wrong.
import pandas as pd  # Lets us read and manage the CSV file as a table of data.
from rapidfuzz import process, fuzz  # Lets us do fuzzy text matching so similar questions can still get answers.


# ------------------------------------------------------------
# SECTION 2: CREATE THE MAIN CHATBOT WINDOW
# In this section, we create the main application window that
# the user will see when the program starts.
# We also set its title, size, and whether it can be resized.
# ------------------------------------------------------------

root = tk.Tk()  # Creates the main application window object.
root.title("FAQ Chatbot")  # Sets the text shown in the title bar of the window.
root.geometry("700x500")  # Sets the starting size of the window to 700 pixels wide and 500 pixels tall.
root.resizable(True, True)  # Allows the user to resize the window both horizontally and vertically.


# ------------------------------------------------------------
# SECTION 3: LOAD THE CSV FILE AND VALIDATE IT
# In this section, we try to open the FAQ CSV file.
# We also check whether the file has the required columns:
# "Question" and "Answer".
#
# Why do we do this?
# Because the chatbot depends on these two columns:
# - the Question column stores the possible user questions
# - the Answer column stores the chatbot responses
#
# If the file is missing or formatted incorrectly, we stop the
# program and show an error popup.
# ------------------------------------------------------------

try:  # Starts a protected block so the program does not crash abruptly if the file cannot be loaded.
    df = pd.read_csv("Chatbot_FAQ_Data.csv")  # Reads the CSV file and stores it in a pandas DataFrame.
    df.columns = df.columns.str.strip()  # Removes extra spaces from column names in case the CSV has messy headers.
except FileNotFoundError:  # Runs only if the CSV file does not exist in the same folder as the Python script.
    messagebox.showerror(
        "File Not Found",
        "Could not find 'Chatbot_FAQ_Data.csv'. Put it in the same folder as this Python file."
    )  # Shows a popup explaining that the file is missing.
    root.destroy()  # Closes the Tkinter window before exiting.
    raise SystemExit  # Completely stops the program.
except Exception as e:  # Runs for any other unexpected file-reading problem.
    messagebox.showerror(
        "Error",
        f"Could not load the CSV file.\n\n{e}"
    )  # Shows a popup with the actual error so the user knows what went wrong.
    root.destroy()  # Closes the Tkinter window before exiting.
    raise SystemExit  # Completely stops the program.

required_columns = {"Question", "Answer"}  # Defines the exact column names that must exist in the CSV.

if not required_columns.issubset(set(df.columns)):  # Checks whether both required columns are present in the file.
    messagebox.showerror(
        "Invalid CSV",
        "The CSV file must contain 'Question' and 'Answer' columns."
    )  # Shows a popup if the CSV does not have the correct structure.
    root.destroy()  # Closes the Tkinter window before exiting.
    raise SystemExit  # Completely stops the program.

df["Question"] = df["Question"].astype(str).str.strip()  # Converts all values in the Question column to clean text.
df["Answer"] = df["Answer"].astype(str).str.strip()  # Converts all values in the Answer column to clean text.
questions = df["Question"].tolist()  # Stores all FAQ questions in a Python list so we can match user input against them.


# ------------------------------------------------------------
# SECTION 4: CREATE THE TITLE AT THE TOP OF THE WINDOW
# In this section, we add a simple heading so the interface
# looks more complete and the user knows what the app is.
# ------------------------------------------------------------

title_label = tk.Label(
    root,  # Places the label inside the main window.
    text="FAQ Chatbot",  # The visible text shown to the user.
    font=("Arial", 18, "bold")  # Makes the title larger and bold for emphasis.
)
title_label.pack(pady=10)  # Displays the title and adds vertical spacing around it.


# ------------------------------------------------------------
# SECTION 5: CREATE THE CHAT DISPLAY AREA
# This is the large box where the conversation will appear.
# The user will see both their own messages and the bot's
# responses here.
#
# Why use ScrolledText?
# Because as more messages appear, the user needs a scrollbar
# to review older messages.
# ------------------------------------------------------------

chat_area = scrolledtext.ScrolledText(
    root,  # Places the chat area inside the main window.
    wrap=tk.WORD,  # Makes long messages wrap nicely at word boundaries.
    font=("Arial", 12),  # Sets a readable font for the conversation.
    state="disabled",  # Makes the chat box read-only so the user cannot type directly into it.
    width=80,  # Sets the width of the chat area.
    height=20  # Sets the height of the chat area.
)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Displays the chat area with spacing and lets it expand with window resizing.


# ------------------------------------------------------------
# SECTION 6: CREATE A BOTTOM FRAME FOR USER INPUT
# This frame acts like a container that holds:
# 1. the text box where the user types
# 2. the send button
#
# Why use a frame?
# It helps organize the layout and keeps the input area separate
# from the main chat area above.
# ------------------------------------------------------------

bottom_frame = tk.Frame(root)  # Creates a frame widget inside the main window.
bottom_frame.pack(padx=10, pady=10, fill=tk.X)  # Displays the frame with spacing and stretches it across the width.


# ------------------------------------------------------------
# SECTION 7: CREATE THE USER INPUT BOX
# This is where the user types a question for the chatbot.
# We also set focus to this box so the user can start typing
# right away without clicking first.
# ------------------------------------------------------------

user_input = tk.Entry(
    bottom_frame,  # Places the input field inside the bottom frame.
    font=("Arial", 12)  # Sets the font style for typed text.
)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))  # Places the input box on the left and lets it stretch across available space.
user_input.focus()  # Automatically puts the keyboard cursor in the input box when the app opens.


# ------------------------------------------------------------
# SECTION 8: DISPLAY MESSAGES IN THE CHAT AREA
# This function is responsible for adding messages to the chat
# window.
#
# Why do we need this function?
# Because both user messages and bot messages should appear
# in the same format and in the same place.
# This avoids repeating the same code multiple times.
# ------------------------------------------------------------

def insert_message(sender, message):  # Takes two inputs: who sent the message and the message text itself.
    chat_area.config(state="normal")  # Temporarily unlocks the chat area so new text can be inserted.
    chat_area.insert(tk.END, f"{sender}: {message}\n\n")  # Adds the message at the bottom of the conversation.
    chat_area.config(state="disabled")  # Locks the chat area again to prevent direct editing by the user.
    chat_area.see(tk.END)  # Automatically scrolls to the newest message so it is always visible.


# ------------------------------------------------------------
# SECTION 9: FIND THE BEST ANSWER FOR THE USER'S QUESTION
# This function tries to match the user's typed question to
# the most similar question stored in the FAQ CSV.
#
# Why do we need fuzzy matching?
# Because users may ask the same thing in different ways.
# For example:
# - "What time do you open?"
# - "When does the store open?"
# - "Store hours?"
#
# These are different strings, but they mean nearly the same thing.
# ------------------------------------------------------------

def get_bot_response(user_text):  # Takes the user's typed message and returns the chatbot's reply.
    if not user_text.strip():  # Checks whether the user typed only spaces or left the input blank.
        return "Please type a question."  # Returns a friendly instruction if nothing useful was typed.

    match = process.extractOne(
        user_text,  # The user's question that we want to compare.
        questions,  # The full list of stored FAQ questions from the CSV.
        scorer=fuzz.token_sort_ratio  # Uses fuzzy matching to score how similar the user's question is to each FAQ question.
    )

    if match is None:  # Checks whether no possible match was found at all.
        return "Sorry, I could not find a matching answer."  # Returns a fallback response if nothing matched.

    best_match, score, _ = match  # Extracts the best matching FAQ question and its similarity score.

    if score < 60:  # Rejects matches that are too weak to trust.
        return "Sorry, I could not find a matching answer."  # Returns a fallback response if similarity is too low.

    answer_rows = df.loc[df["Question"] == best_match, "Answer"]  # Finds the answer that belongs to the matched FAQ question.

    if answer_rows.empty:  # Checks whether an answer was actually found for that question.
        return "Sorry, I found a similar question, but no answer was available."  # Returns a fallback response if the answer is missing.

    return answer_rows.iloc[0]  # Returns the first matching answer from the Answer column.


# ------------------------------------------------------------
# SECTION 10: HANDLE SENDING A MESSAGE
# This function runs when the user:
# 1. clicks the Send button
# 2. presses the Enter key
#
# It does several things:
# - reads the user's question
# - shows it in the chat area
# - clears the text box
# - gets the bot's answer
# - displays the bot's answer
# ------------------------------------------------------------

def send_message(event=None):  # event=None allows this function to work for both button clicks and Enter key presses.
    user_text = user_input.get().strip()  # Reads the text currently typed in the input box and removes extra spaces.

    if not user_text:  # Checks whether the input is empty after trimming spaces.
        return  # Stops the function if there is nothing to send.

    insert_message("You", user_text)  # Displays the user's message in the chat area.
    user_input.delete(0, tk.END)  # Clears the input box so the user can type the next question.

    bot_response = get_bot_response(user_text)  # Calls the matching function to get the chatbot's answer.
    insert_message("Bot", bot_response)  # Displays the chatbot's answer in the chat area.


# ------------------------------------------------------------
# SECTION 11: CREATE THE SEND BUTTON
# This button gives the user a clear way to submit a question.
# When clicked, it runs the send_message function.
# ------------------------------------------------------------

send_button = tk.Button(
    bottom_frame,  # Places the button inside the bottom frame.
    text="Send",  # Text shown on the button.
    font=("Arial", 12),  # Makes the button text readable.
    command=send_message,  # Tells Tkinter which function to run when the button is clicked.
    width=10  # Gives the button a fixed width so it looks neat.
)
send_button.pack(side=tk.RIGHT)  # Places the button on the right side of the input frame.


# ------------------------------------------------------------
# SECTION 12: ALLOW THE ENTER KEY TO SEND MESSAGES
# This makes the chatbot easier to use because the user does
# not have to click the Send button every time.
# Pressing Enter will do the same thing.
# ------------------------------------------------------------

user_input.bind("<Return>", send_message)  # Links the Enter key to the send_message function.


# ------------------------------------------------------------
# SECTION 13: SHOW A STARTING MESSAGE FROM THE CHATBOT
# This is the bot's first greeting so the window does not look
# empty when it opens.
# It also tells the user what the chatbot is meant to do.
# ------------------------------------------------------------

insert_message("Bot", "Hello! Ask me a question from the FAQ data.")  # Adds the starting bot greeting to the chat area.


# ------------------------------------------------------------
# SECTION 14: KEEP THE APPLICATION RUNNING
# Tkinter applications need mainloop() to stay open and keep
# listening for user actions like typing, clicking, and resizing.
#
# Without this line, the window would appear and then close
# immediately.
# ------------------------------------------------------------

root.mainloop()  # Starts the event loop so the chatbot window remains active and interactive.