from openai import OpenAI
from dotenv import load_dotenv
import os, time, pprint
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

assistant_id = "asst_aCkydg8wjPVbC1TfAiy610Vz"
client = OpenAI(api_key=OPENAI_API_KEY)
analyze_post_prompt_template = """
    Here is info on a LinkedIn lead: 
    <<NAME>> 
    Location: <<LOCATION>> 
    <<HEADLINE>>
    
    Here is a post created by the lead: 
    <<TIMESINCEPOSTED>>: 
    <<POSTTEXT>> 
    
    Dissect this post for natural engagement opportunities
"""

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
def create_new_thread_and_run_initial_analysis(agent_id, lead_name, lead_loc, lead_headline, time_since_posted, post_text, role="user"):
    message = analyze_post_prompt_template.replace("<<NAME>>", lead_name).replace("<<LOCATION>>", lead_loc).replace("<<HEADLINE>>", lead_headline).replace("<<TIMESINCEPOSTED>>", time_since_posted).replace("<<POSTTEXT>>", post_text)
    run = client.beta.threads.create_and_run(
        assistant_id=agent_id,
        thread={
            "messages": [
            {"role": role, "content": message}
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
    agent = get_agent(assistant_id)
    lead_name = "Rahul Pandey"
    lead_loc = "Stanford, CA"
    lead_headline = "Staff Engineer. Building joinTaro.com to help engineers find career success. Taro, Meta, Pinterest, Stanford."
    time_since_posted = "Posted 3h"
    post_text = """
    Apparently, I hit the connection limit on LinkedIn 😭 

    I can't accept invitations to connect now unless I boot an existing connection. Apologies if your connection request has been pending. (Please help me out by adding a message in your request -- I always prioritize those.)

    Is there an easy way to remove my connection with older accounts that may not be active, or are likely bots? I'd love a solution to this, free or paid 🙏🏽

    """
    analysis = create_new_thread_and_run_initial_analysis(assistant_id, lead_name, lead_loc, lead_headline, time_since_posted, post_text)
    print(analysis)

    