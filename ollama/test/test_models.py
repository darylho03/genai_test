import ollama

user_prompt = input("Please enter your question: ")
with open("llama3_2.txt", "w") as f:
    response = ollama.chat(
        model='llama3.2:latest',
        messages=[
            {
                'role': 'user',
                'content': user_prompt,
            },
        ],
    )
    f.write(response['message']['content'])

with open("deepseek-r1.txt", "w") as f:
    response = ollama.chat(
        model='deepseek-r1:1.5b',
        messages=[
            {
                'role': 'user',
                'content': user_prompt,
            },
        ],
    )
    f.write(response['message']['content'])

with open("gemma3.txt", "w") as f:
    response = ollama.chat(
        model='gemma3:1b',
        messages=[
            {
                'role': 'user',
                'content': user_prompt,
            },
        ],
    )
    f.write(response['message']['content'])

with open("qwen3.txt", "w") as f:
    response = ollama.chat(
        model='qwen3:1.7b',
        messages=[
            {
                'role': 'user',
                'content': user_prompt,
            },
        ],
    )
    f.write(response['message']['content'])

