# Improper Output Handling

The LLM10: Improper Output Handling risk highlights the danger when LLMs return unfiltered or unsanitized outputs that can be manipulated by attackers, leading to unintended behavior or leakage of sensitive data. The guidance suggests ensuring output is appropriately sanitized, and that prompt inputs are handled securely to prevent attackers from crafting malicious requests that influence the model's responses.

## Challenge Objective
Purchase an item to solve the challenge

# Solution

  
- Access the application at http://127.0.0.1:5010

- Register an account and login

- The balance is 0 and we are not able to purchase any item

- Click on AI Assistant and it opens chat window.

- As mentioned in description, application interact with database through AI Assistant, let's try to use prompts to fetch data from database. 

- Prompt to list users, and update balance of the logged in user

![1](https://github.com/R3dShad0w7/PromptMe/blob/main/solutions/LLM05_ImproperOutputHandling/1.jpg)

- Now, that we have balance in our account, we can purchase itema dn solve the challenge

![2](https://github.com/R3dShad0w7/PromptMe/blob/main/solutions/LLM05_ImproperOutputHandling/2.jpg)

- And there we have a flag and challenge is solved. 
# Prevention and Mitigation Strategies
As OWASP Suggests,
- Treat the model as any other user, adopting a zero-trust approach, and apply proper input validation on responses coming from the model to backend functions.
- Follow the OWASP ASVS (Application Security Verification Standard) guidelines to ensure effective input validation and sanitization.
  
For this specific case, 
- Parameterized queries prevent SQL Injection by ensuring that user inputs are treated as data rather than executable SQL code. However, in such LLM-driven SQL execution, parameterized queries alone are not effective as it generates full SQL queries rather than taking specific values from user prompt. 
- Allow only safe SQL commands (e.g., SELECT) using strict allowlist
```
if not generated_sql.lower().startswith("select"):
    return jsonify({"reply": "❌ Only SELECT queries are allowed for this challenge."})
```
- It is advisable to restrict UPDATE/ALTER/DROP/DELETE kind of modification statements when using SQL Integrations

