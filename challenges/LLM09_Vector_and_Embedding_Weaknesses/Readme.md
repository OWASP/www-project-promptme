# LLM09: Vector and Embedding Weaknesses

Vectors and embeddings vulnerabilities present significant security risks in systems utilizing Retrieval Augmented Generation (RAG) with Large Language Models (LLMs). Weaknesses in how vectors and embeddings are generated, stored, or retrieved can be exploited by malicious actions (intentional or unintentional) to inject harmful content, manipulate model outputs, or access sensitive information.

In this challenge, participants will exploit a semantic collision vulnerability in an LLM-powered web application. The application uses a vector embedding model to match user queries with preloaded hints in a vector store, generating a response using an LLM. Participants must craft a query that semantically matches the hints stored in the vector store, causing the LLM to generate a hidden URL for a secret flag. Successfully triggering the LLM to reveal the flag URL demonstrates an understanding of how vector embeddings can be manipulated to generate unintended outputs.

## Challenge Objective

Identify the location of flag, and accordingly create a embedding payload to submit to vector store. Draft prompt to identify the URL containing flag.

Application URL: http://127.0.0.1:5009

**Hint:** Understand the application response and accordingly craft a prompt to submit to vector store, which performes similarility match and give flag URL.



