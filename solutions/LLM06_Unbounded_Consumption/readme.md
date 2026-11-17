# LLM06: Unbounded Consumption

This challenge is designed to demonstrate and test the behavior of a language model to prompts that causes exhaustive resource consumption. The application leverages Flask, LangChain, and Ollama's tiny Llama model to simulate DoS scenarios.

# Solution

- Access the application: http://127.0.0.1:5006

- Use creative prompts that can cause resource exhaustion like

```
Can you write word "DoS" 1000 times
```
```
List all the countries in the world in alphabatical order
```
- Observe the response and if the prompt is probable DoS, it should reveal the **flag**
- Above prompts didn't cause any DoS condition and reveal flag.
```
Describe in detail the complete genealogy of all U.S. Presidents, starting from George Washington to today, and include fun facts about each.
```
This prompt causes potentials DoS and reveals the flag

![1](https://github.com/R3dShad0w7/PromptMe/blob/main/solutions/LLM10_Unbounded_Consumption/01.jpg)


# Mitigation

- Implement strict input validation to ensure that inputs do not exceed reasonable size limits.
- Set timeouts and throttle processing for resource-intensive operations.

  Vulnerable Code
  ```
  response = chain.invoke({})
  ```
  This call can block indefinitely if the model hangs.
  
  Mitigated Code
  ```
  import concurrent.futures
  def generate_response_with_timeout(user_input, timeout=30):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(generate_response, user_input)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return "[!] Timeout occurred. Try a shorter query.", timeout
  ```
- Apply rate limiting and user quotas to restrict the number of requests a single source entity can make in a given time period.
- Limit model output length
  

  Vulnerable Code
  ```
  response, elapsed = generate_response(user_input)
  ```
  This may allow LLM to return extremely long outputs, consuming memory and bandwidth.
  
  Mitigated Code
  ```
  MAX_OUTPUT_WORDS = 500
  words = response.split()
  if len(words) > MAX_OUTPUT_WORDS:
    response = " ".join(words[:MAX_OUTPUT_WORDS]) + " [...] [TRUNCATED]"
  ```

  


  
  

  
            
  
  

