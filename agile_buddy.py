import os
import time
import requests
import datetime
from plyer import notification
import signal
import pathlib
import threading

OLLAMA_API_URL = "http://localhost:11434/api/generate"
chat_system = """You are an LLM made to assist with agile workflow, 
        the idea is to capture information of the what tasks the user did today as an assistant asking what is needed.
        be direct and disconsider that the user can end abruptly"""
summary_system = """You are an LLM made to assist with agile workflow, the idea 
is to list what the user's day in bullet points. So he can use this information in the next standup"""
daily_summaries_folder = "daily_summaries"
notes_folder = "notes"

def check_summary_done():
    # Check if todays summary is already done
    summary_done = False
    paths = pathlib.Path(daily_summaries_folder).glob('*.txt')
    for path in paths:
        if path.stem.removeprefix("summary_")[:-6] == datetime.datetime.now().strftime("%d_%m_%Y"):
            summary_done = True
            break
    return summary_done

def chat_with_model(user_input, system=""):
    payload = {
        "model": "llama3.2",
        "prompt": user_input,
        "system": system,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "No response")
    return "Error connecting to the model."

def send_notification():
    notification.notify(
        title="Daily Chat Reminder",
        message="Hey! How was your day? Let's chat. 😊",
        timeout=10
    )

def check_time():
    while True:
        current_hour = datetime.datetime.now().hour
        if 16 <= current_hour < 17:
            get_end_of_the_day_info()
            time.sleep(3600)  # Sleep for an hour to avoid multiple triggers
        time.sleep(60)  # Check every minute
            
def get_end_of_the_day_info():
    summary_done = check_summary_done()
    if summary_done:
        print("Today's summary already done")
        return
    
    # Setup conversation
    conversation_log = "Hey! What you did today?[Note: type bye or exit to exit]"
    print(conversation_log)
    
    # Get user response
    user_input = input("> ")  
    conversation_log += "User: " + user_input + "\n"
    
    while user_input.lower() not in ["exit", "bye"]:
        response = chat_with_model(conversation_log, chat_system)
        print("🤖:", response)
        user_input = input("> ")  # Continue conversation
        conversation_log += "User: " + user_input + "\n"
    # End of conversation
    print("Good night! See you tomorrow. 😊")
    print("")
    
    # Generate summary
    summary_prompt = "This is the end of the day conversation with the user: " + conversation_log + "Please list what the user did in bullet points."
    summary = chat_with_model(summary_prompt, summary_system)
    
    # Save summary to file
    current_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
    os.makedirs(daily_summaries_folder, exist_ok=True)
    with open(f"{daily_summaries_folder}/summary_{current_time}.txt", "w") as f:
        f.write(summary)
    print("Summary:", summary)

def take_note(note_title):
    conversation_log = "Hey! Input your fast note"
    note_content = input("> ")
    os.makedirs(notes_folder, exist_ok=True)
    current_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
    with open(f"{notes_folder}/{note_title}_{current_time}.txt", "w") as f:
        f.write(note_content)

def generate_summary(initial_day, end_day):
    # Parse days
    initial_day = datetime.datetime.strptime(initial_day, "%d_%m_%Y")
    end_day     = datetime.datetime.strptime(end_day, "%d_%m_%Y")
    
    # Get all summaries within days
    paths = pathlib.Path(daily_summaries_folder).glob('*.txt')
    context = ""
    for path in paths:
        file_date_raw = path.stem.removeprefix("summary_")[:-6] # Format is dd_mm_yyyy
        file_date = datetime.datetime.strptime(file_date_raw, "%d_%m_%Y")
        if file_date >= initial_day and file_date <= end_day:
            with open(path, "r") as f:
                context += file_date_raw + "\n"
                context += f.read()
                
    # Generate summary
    summary_prompt = context + "Please list what the user did in bullet points for the given days."
    summary = chat_with_model(summary_prompt, summary_system)
    print("Summary:", summary)

def search_task(phrase):
    print("Not implemented yet")

interrupt_flag = threading.Event()

def check_time():
    while True:
        current_hour = datetime.datetime.now().hour

        summary_done = check_summary_done()
        if current_hour >= 18 and current_hour < 19 and not summary_done:
            # Warn the user that we expect his input
            send_notification()
            time.sleep(3600)  # Sleep for an hour to avoid multiple triggers
        time.sleep(60)  # Check every minute

def main():
    # Print first usage instructions
    print("Welcome to Agile Buddy! I will help you to keep track of your daily work.")
    print("At an specific time of the day I will ask how was your day, list your tasks and save to a file")
    print("otherwise you can take notes, search for information or ask for a standup summary.")
    print("Just type:")
    print("    - end_day: take notes of your day")
    print("    - note <note title>: to take fast notes")
    print("    - summary <initial_day[dd_mm_yyyy]> <end_day[dd_mm_yyyy]>: to get a summary of your tasks")
    print("    - search <phrase>: to search for a specific task")
    print("    - exit: to end program")
    
        # Start the time checking thread
    time_thread = threading.Thread(target=check_time)
    time_thread.daemon = True
    time_thread.start()
    
    while True:
        # Check user input
        result = input("Enter something:\n")
        if result != "":
            if result.lower() == "exit":
                break
            elif result.lower() == "end_day":
                get_end_of_the_day_info()
            elif result.lower().startswith("note"):
                note_title = result.split(" ", 1)[1]
                print("Taking note:", note_title)
                take_note(note_title)
            elif result.lower().startswith("summary"):
                initial_day, end_day = result.split(" ", 1)[1].split(" ")
                print("Getting summary from", initial_day, "to", end_day)
                generate_summary(initial_day, end_day)
            elif result.lower().startswith("search"):
                phrase = result.split(" ", 1)[1]
                print("Searching for:", phrase)
                search_task(phrase)

if __name__ == "__main__":
    main()