# LLM08: Hidden Context Exposure

> In the OWASP Top 10 for LLM Applications 2026, *System Prompt Leakage* (LLM07:2025) was renamed **Hidden Context Exposure** and broadened to cover everything an application places in front of the model without the user seeing it: system prompts, tool definitions, retrieved documents, memory and other injected context.

This challenge showcases a Hidden Context Exposure vulnerability, where sensitive information—such as an API key—is embedded within the system prompt, the most common piece of hidden context. Participants must use prompt injection techniques to extract the hidden data from the model's responses.

---

## Challenge Objective

Large Language Models (LLMs) are often guided by **system prompts** that influence their behavior. If these prompts include sensitive information (e.g., credentials, secrets, API keys), and if an attacker can manipulate or indirectly query the model's context, that information can leak.

This CTF challenge simulates such a scenario:
- The LLM is initialized with a system prompt that embeds a secret `API_KEY`.
- The model is instructed never to reveal it.
- Your mission: **get the model to leak the key through creative prompting**.

Application URL: http://127.0.0.1:5008

**Hint:** Use Prompt Injection/Jailbreak techniques 



