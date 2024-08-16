# OpenAI Assistants API Template For Telegram

**To build out profitable Telegram Bots with this template, please contact [@AutoNate](https://t.me/@AutoNate).**

You will learn how to read various markets to quickly discover their patterns, stressors and relaxers. Then you will use ChatGPT to configure a plan that innovates their patterns. We will then automate this plan and deliver it via a Telegram bot. This approach will not only make you filthy rich, but also helps the people in those markets! 

This template serves as your frontend and backend for those automations!

With Telegram having over 1 billion active users a month, you are essentially bringing the power of AI and automations to the everyday person. You're doing this by learning how to build innovative solutions to their current patterns, and then by easily delivering the solution via the trusted Telegram platform.

Let's get a bag 😎

Hit me up!

## Project Overview

**THE** Telegram bot template you’ve been looking for. One template, infinite possibilities. 

Powered by Python and OpenAI, this setup isn’t just about building bots—it’s about creating experiences. 

Need a bot to solve niche problems? Automate tasks? This template’s got your back. 

The architecture is flexible, scalable, and ready to monetize.

We’ve handled the heavy lifting—AI functions, modular design, easy extensions. 

All you need is creativity!

Plug in your ideas, tweak the code, and let the bot do the rest.

## Installation Instructions

1. Clone the repo -> `git clone https://github.com/telegram-bot-builders/OpenAI-Assistants-Telegram-Template.git tele-bot`
2. cd into the newly created directory -> `cd tele-bot`
3. create new venv -> `python -m venv env` or `python3 -m venv env`
4. initiate venv -> Unix: `source env/bin/activate` Windows: `env\Scripts\activate`
5. install requirements with -> `pip install -r requirements.txt`
6. create .env file -> `touch .env`
7. update following values in the .env file
   - OPENAI_API_KEY=sk-xxxxxxx
   - TELEGRAM_BOT_TOKEN=xxxxxx
   - ASSISTANT_ID=xxxxx
8. start bot -> `python bot.py`

## How To Extend The Code

Now that you've got the basics down, it’s time to level up by extending the bot’s functionality. Whether you're looking to add new command handlers, integrate advanced AI features, or introduce entirely new modules, this template is designed for easy expansion. Here's how you can get started:

#### 1. **Adding New Command Handlers in `bot.py`**

When you want your bot to handle more commands, like `/stats` or `/feedback`, you’ll need to create new handlers in `bot.py`. 

**Example:**
- Add a new command handler by defining a function and registering it in the `setup_handlers()` method.

```python
async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Example of what you could do here: fetch and send user stats
    stats_message = "Here are your stats..."
    await update.message.reply_text(stats_message)

def setup_handlers(self):
    self.application.add_handler(CommandHandler('start', self.start))
    self.application.add_handler(CommandHandler('help', self.help))
    self.application.add_handler(CommandHandler('engage', self.engage))
    self.application.add_handler(CommandHandler('stats', self.stats))  # New command handler added
    self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
```

**Why This Matters:**
- Adding new commands allows you to respond to specific user needs or provide additional functionality like gathering feedback, showing statistics, or anything else your niche might require.

#### 2. **Extending AI Features in `ai.py`**

The `ai.py` file is your go-to for all things AI-related. If you've identified specific patterns or problems in your market, this is where you implement solutions that leverage AI.

**Example:**
- You could create a new AI function that provides personalized recommendations based on user input.

```python
def generate_recommendations(thread_id, user_input):
    # Imagine this function uses OpenAI to provide personalized recommendations
    response = client.beta.threads.messages.create(
        thread_id,
        role="assistant",
        content=f"Based on what you told me, here's what I'd recommend: {user_input}"
    )
    return response.content
```

- Then, in `bot.py`, connect this new function to a handler.

```python
async def recommend(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    recommendation = generate_recommendations(self.current_thread_id, user_input)
    await update.message.reply_text(recommendation)

def setup_handlers(self):
    self.application.add_handler(CommandHandler('recommend', self.recommend))  # Handler for recommendations
```

**Why This Matters:**
- Extending AI functionality allows you to deliver more sophisticated, context-aware responses that can address specific user needs in creative ways.

#### 3. **Adding New Modules and Connecting Them**

Want to add a completely new feature that doesn’t quite fit into `bot.py` or `ai.py`? No problem—just create a new module. After creating it, import the functionality into `bot.py` and link it up.

**Example:**
- Suppose you create a new file `analytics.py` that handles all data analytics for your bot. 

```python
# analytics.py
def analyze_user_data(user_id):
    # Your custom analytics logic here
    return f"Analytics for user {user_id}: ..."
```

- You can then import this function into `bot.py` and add it to a handler.

```python
from analytics import analyze_user_data

async def show_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    analytics_data = analyze_user_data(user_id)
    await update.message.reply_text(analytics_data)

def setup_handlers(self):
    self.application.add_handler(CommandHandler('analytics', self.show_analytics))  # New analytics handler
```

**Why This Matters:**
- Adding new modules lets you keep the codebase organized and modular, making it easier to maintain and scale. Whether you're integrating external APIs, adding new data processing layers, or implementing custom user interaction features, this approach keeps everything clean and manageable.

---
## Updates Coming Soon

Exciting updates are on the horizon! We're implementing OpenAI Assistants Function Calling by **8/23/2024**. This will bring even more power and flexibility to your Telegram bot, allowing the AI to execute functions you define directly within your code.

### What’s Coming:

- **New Files**:
  - **`assistant_functions.py`**: This file will house the functions that you want your OpenAI assistant to use.
  - **`openai_schemas.py`**: This file will define the OpenAI function schemas, mapping out how each function should be structured.

**Example:**

- A function like `get_weather(location: str) -> str` could look like this:

  ```python
  def get_weather(location: str) -> str:
      return f"The weather is 89 degrees in {location}"
  ```

- And the corresponding schema in `openai_schemas.py` might look like:

  ```json
  {
    "name": "get_weather",
    "description": "Gets the weather from the location.",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The location the user wants the weather for."
        }
      },
      "required": [
        "location"
      ]
    }
  }
  ```

### Updates to `ai.py`:

We’ll also be updating `ai.py` to integrate this new functionality:

- **Function Management**: 
  - Methods for adding and removing functions from the OpenAI assistant.
  
- **Enhanced Messaging Functionality**:
  - We’ll update the messaging code to handle the `requires_action` state. This will enable your bot to execute functions based on the assistant's requests.

**Example Code Update in `ai.py`:**

```python
elif run_status.status == 'requires_action':
    print("Function Calling")
    required_actions = run_status.required_action.submit_tool_outputs.model_dump()
    print(required_actions)
    tool_outputs = []
    import json
    for action in required_actions["tool_calls"]:
        func_name = action['function']['name']
        arguments = json.loads(action['function']['arguments'])
        
        if func_name == "next_move":
            output = next_move(action=arguments['action'])
            print(output)
            tool_outputs.append({
                "tool_call_id": action['id'],
                "output": output
            })
        else:
            raise ValueError(f"Unknown function: {func_name}")
        
    print("Submitting outputs back to the Assistant...")
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )
```

This update ensures that the bot can dynamically handle function calls, making your AI assistant more interactive and capable of performing specific tasks directly in response to user commands.

Stay tuned! These updates are going to unlock even more potential for your bot, making it a more powerful tool for any market or community you’re targeting.
## 1-on-1 Python Tutoring

Looking to master Python, build AI-driven Telegram bots, or just level up your coding skills? 

I'm here to help!

I offer personalized, 1-on-1 Python tutoring sessions via Telegram. 

Whether you're a beginner or looking to dive deeper into advanced topics, I've got you covered.

**Get in touch:** [@AutoNate](https://t.me/@AutoNate) on Telegram.

Let's get you coding like a pro!

## About the Author

Hey, I'm Nate Baker, a seasoned developer and AI enthusiast with a passion for building innovative solutions. Over the years, I've honed my skills in Python and AI, crafting tools that not only solve problems but also open new possibilities for businesses and individuals alike.

I specialize in creating AI-driven Telegram bots, automating processes, and turning complex problems into manageable, profitable solutions. When I'm not coding, I'm usually sharing my knowledge through tutoring or contributing to open-source projects.

**Connect with me on LinkedIn:** [Nate Baker](https://www.linkedin.com/in/nate-gpt-expert/)

## Additional Resources

Looking for more? Check out these resources to help you get the most out of this template:

- [MeetUp.com](https://www.meetup.com/market-matrix/) - Weekly Zoom Meet Up!

## Contributing

Contributions are welcome! If you've got ideas, code improvements, or new features to add, feel free to fork the repo and submit a pull request. Let’s make this template even better together!

For major changes, please open an issue first to discuss what you would like to change.

**Fork the repo:** [OpenAI Assistants API Template For Telegram](https://github.com/telegram-bot-builders/OpenAI-Assistants-Telegram-Template)

## License

This project is licensed under the MIT License. See the [LICENSE](#) file for details.


