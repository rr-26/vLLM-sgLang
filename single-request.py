from openai import OpenAI
from mistralai import Mistral
import anthropic
import os
import time
from dotenv import load_dotenv
from termcolor import colored

# Load environment variables
load_dotenv()

# Retrieve the env variables
model = os.getenv('MODEL')
api_endpoint = os.getenv('API_ENDPOINT', '')

openai_api_base = api_endpoint + '/v1'

# FYI, a runpod api key only needs to be set if using serverless.
api_key = os.getenv('API_KEY') if os.getenv('API_KEY') is not None else "EMPTY"

# Initialize the appropriate client based on the model
if 'mistral-large-latest' in model or 'open-mistral-nemo' in model:
    client = Mistral(api_key=api_key)
elif 'claude' in model.lower():
    client = anthropic.Anthropic(api_key=api_key)
else:
    print("Using OpenAI style client")
    client = OpenAI(
        api_key=api_key,
        base_url=openai_api_base,
    )

def chat_completion_request(messages, client):
    start_time = time.time()  # Start timing

    if isinstance(client, Mistral):
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=0.01,
            max_tokens=200
        )
    elif isinstance(client, anthropic.Anthropic):
        chat_response = client.messages.create(
            model=model,
            messages=messages,
            temperature=0.01,
            max_tokens=200
        )
    else:
        chat_response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.01,
            max_tokens=200
        )

    print(chat_response)

    response_time = time.time() - start_time  # Calculate response time

    # Extract the completion text from the response
    if isinstance(client, anthropic.Anthropic):
        completion_text = chat_response.content[0].text
        prompt_tokens = chat_response.usage.input_tokens
        tokens_generated = chat_response.usage.output_tokens
    else:
        completion_text = chat_response.choices[0].message.content if chat_response.choices else None
        prompt_tokens = chat_response.usage.prompt_tokens if completion_text else 0
        tokens_generated = chat_response.usage.completion_tokens if completion_text else 0

    # Calculate tokens per second
    tokens_per_second = tokens_generated / response_time if response_time > 0 else 0

    # Print time taken and tokens per second
    print(f"Total Time Taken: {response_time:.2f} seconds")
    print(f"Prompt tokens: {prompt_tokens:.2f}")
    print(f"Tokens generated: {tokens_generated:.2f}")
    print(f"Tokens per Second: {tokens_per_second:.2f}")

    return completion_text

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        color = role_to_color.get(message["role"], "grey")
        print(colored(f"{message['role']}: {message['content']}\n", color))

# Test the function
messages = [
    {"role": "user", "content": "Write a long essay on the topic of spring."}
    # {"role": "user", "content": "What is one plus one?"}
]

chat_response = chat_completion_request(messages, client)
messages.append({"role": "assistant", "content": chat_response})

# pretty_print_conversation(messages)