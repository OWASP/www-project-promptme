# LLM10 - Improper Output Handling

Improper Output Handling occurs when an LLM generates outputs that are not properly validated or constrained, potentially leading to security vulnerabilities. Attackers may exploit this to manipulate downstream systems or gain unauthorized access.

This challenge demonstrates OWASP LLM Risk LLM10: Improper Output Handling in the context of an e-commerce application.
Participants interact with a chatbot that is integrated with a SQLite3 database. Upon registration, users receive 0 credits. By manipulating the chatbot's output behavior, participants must trick it into increasing their account credit and use it to purchase an item to solve the challenge.

## Challenge Objective

Once register, you login with 0 credits. Find a flaw in the application to buy credit and purchase an item to solve the challenge. 

Application URL: http://127.0.0.1:5010

**Hint:** Use prompts that can translate to SQL statements and update balance. 


