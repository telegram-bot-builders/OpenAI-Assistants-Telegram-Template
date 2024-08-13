from openai import OpenAI
from dotenv import load_dotenv
import os, time, pprint
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

assistant_id = os.getenv("ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)

# Get the agent
def get_agent(agent_id):
    return client.beta.assistants.retrieve(agent_id)

# create a new thread
def create_thread():
    empty_thread = client.beta.threads.create()
    return empty_thread

# retreive a thread
def get_thread(thread_id):
    return client.beta.threads.retrieve(thread_id)

# create a message for a thread
def create_message_in_thread(thread_id, role, message):
    thread_message = client.beta.threads.messages.create(
        thread_id,
        role=role,
        content=message,
    )
    return thread_message

# list messages in a thread
def list_messages_in_thread(thread_id):
    thread_messages = client.beta.threads.messages.list(thread_id, limit=10)
    return thread_messages.data

# run a message thread
def run_message_thread(thread_id, agent_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=agent_id
    )
    run_status = run.status
    print(run_status)
    print(f"Thread ID: {run.thread_id}")
    message = None
    while run.status != "completed":
        print(f'Run Status: {run.status}')
        if run.status == "incomplete" or run.status == "expired" or run.status == "cancelled":
            print("Run failed.")
            return None
        run = get_run(run.thread_id, run.id)
        time.sleep(3)
    message = list_messages_in_thread(run.thread_id)[0].content[0].text.value
    return message

# get a run
def get_run(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )
    return run

# create new thread and run initial message
def create_new_thread_and_run(agent_id, msg_text, role="user"):
    run = client.beta.threads.create_and_run(
        assistant_id=agent_id,
        thread={
            "messages": [
            {"role": role, "content": msg_text}
            ]
        }
    )
    run_status = run.status
    print(run_status)
    print(f"Thread ID: {run.thread_id}")
    message = None
    while run.status != "completed":
        print(f'Run Status: {run.status}')
        if run.status == "incomplete" or run.status == "expired" or run.status == "cancelled":
            print("Run failed.")
            return None
        run = get_run(run.thread_id, run.id)
        time.sleep(3)


    message = list_messages_in_thread(run.thread_id)[0].content[0].text.value
    return message, run.thread_id, run.id


if __name__ == "__main__":
    pass

    