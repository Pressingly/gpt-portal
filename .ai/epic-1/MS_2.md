Story Definition

Target Review due date:

, Target Approval date:

Apr 7, 2025

Author: Grace Hoang ,Status:
Apr 4, 2025
Reviewers: ; Approver:

Accepted

,

Title: Display Model Cost and Benefits

Epic: Model Selection

MVP Scope: System / Subsystem / Component / Item / Subitem

Description: sers need transparency around what each model offers — both in terms of
pricing and strengths (e.g., faster inference, longer context, multilingual fluency). This is
critical to empowering informed choices and aligning model usage with query intent
(e.g., creative writing vs. math-heavy queries).

Narrative:

●  As a user, I want to understand the cost and the benefits of each LLM that I am

selecting.
Acceptance Criteria:

●  User clicks on “Learn more about each LLM”
●  Each model listed for selection displays its estimated cost per query (based on

token count).

●  Each model displays a summary of its company, tier, model, pricing, and core

strengths or differentiators. Here is the info for our selected LLMs:

1.  GPT-4o

○  Company: OpenAI
○  Tier: Standard
○  Model Name: GPT-4o
○  Pricing:

■
Input Tokens: $2.50 per million tokens
■  Output Tokens: $10.00 per million tokens

○  Best Use Cases: General-purpose tasks requiring a balance

between performance and cost, such as content creation, customer
support, and data analysis.

2.  GPT-4o-mini

○  Company: OpenAI
○  Tier: Value
○  Model Name: GPT-4o-mini
○  Pricing:

1.  Input: $0.15 / 1M tokens

2.  Output: $0.60 / 1M tokens

○  Best Use Cases: Suitable for applications requiring faster

responses and lower latency, such as real-time chat applications
and lightweight content generation.

3.  GPT-4.5

○  Company: OpenAI
○  Tier: Pro
○  Model Name: GPT-4.5
○  Pricing:

■

Input Tokens: $75 per million tokens
Output Tokens: $150 per million tokens

○  Best Use Cases: High-stakes applications requiring nuanced and
emotionally intelligent interactions, such as premium customer
support, mental health coaching, and complex content creation.

1.  Gemini 2.0 Flash

○  Company: Google
○  Tier: Standard
○  Model Name: Gemini 2.0 Flash

Pricing:
■
Input Tokens: Approximately $0.15 per million tokens
■  Output Tokens: Approximately $0.60 per million tokens

○  Best Use Cases: Ideal for high-volume tasks requiring processing

of extensive content, such as large-scale data analysis and
document processing.

2.  Gemini 2.0 Flash Lite

○  Company: Google
○  Tier: Value

Model Name: Gemini 2.0 Flash Lite
Pricing:

1.  Input: $0.075 / 1M tokens
2.  Output: $0.30 / 1M tokens

○  Best Use Cases: Suitable for applications requiring efficient

processing with lower resource consumption, such as mobile
applications and embedded systems.

3.  Gemini 2.0 Pro

○  Company: Google
○  Tier: Pro
○  Model Name: Gemini 2.0 Pro

○  Pricing:

1.  Input: $2.50 / 1M tokens
2.  Output: $10 / 1M tokens

○  Best Use Cases: Advanced AI applications requiring higher

performance and capabilities, such as complex data modeling and
enterprise-level solutions.

1.  Claude 3.7 Sonnet

○  Company: Anthropic
○  Tier: Standard
○  Model Name: Claude 3.7 Sonnet
○  Pricing:

■
Input Tokens: $3.00 per million tokens
■  Output Tokens: $15.00 per million tokens

○  Best Use Cases: Excels in complex problem-solving, particularly in
math and coding tasks, as well as agentic coding and legal tasks.

2.  Claude 3.5 Haiku

○  Company: Anthropic

○  Tier: Value
○  Model Name: Claude 3.5 Haiku
○  Pricing:

1.  Input: $0.80 / 1M tokens
2.  Output: $4 / 1M tokens

○  Best Use Cases: Designed for general-purpose tasks requiring a
balance between performance and cost, such as content creation
and customer support.

3.  Claude 3 Opus

○  Company: Anthropic
○  Tier: Pro
○  Model Name: Claude 3 Opus
○  Pricing:

1.  Input: $15 / 1M tokens
2.  Output: $75 / 1M tokens

○  Best Use Cases: Suitable for advanced AI applications requiring

higher performance and capabilities, such as complex data analysis
and enterprise solutions.

●  Llama 3.1 70B

○  Company: META
○  Tier: Standard
○  Model Name: Llama 3.1 70B
○  Pricing:

 Input: $2.68 / 1M tokens
●
●  Output: $3.54 / 1M tokens

○  Best Use Cases: Designed for commercial hardware, suitable for
applications requiring substantial processing power, such as
research and development in AI.

Llama 3.2 11B

○  Company: META
○  Tier: Value
○  Model Name: Llama 3.2 11B

Pricing:

1.  Input: $0.37 / 1M tokens
2.  Output: $0.37 / 1M tokens

○  Best Use Cases: Suitable for applications requiring a balance

between performance and resource efficiency, such as small to
medium-scale AI tasks, educational tools, and prototype
development.

2.  Llama 3.1 405B

○  Company: META
○  Tier: Pro
○  Model Name: Llama 3.1 405B

○  Pricing:

1.  Input: $0.90 / 1M tokens
2.  Output:

○  Best Use Cases: Best suited for high-level research and

applications requiring extensive computational power, such as
advanced AI research, large-scale data analysis, and complex
simulations.

1.  Sonar Pro

○  Company: Perplexity

○  Tier: Standard

○  Model Name: Sonar Pro

Pricing:
■
Input Tokens: $3 per million tokens
■  Output Tokens: $15 per million tokens
■  Price per 1,000 Requests: $5

○  Best Use Cases: Advanced search applications requiring deep

content understanding and handling of complex queries, such as
in-depth research tasks and comprehensive information retrieval.

2.  Sonar

○  Company: Perplexity
○  Tier: Value
○  Model Name: Sonar
○  Pricing:

■
Input Tokens: $1 per million tokens
■  Output Tokens: $1 per million tokens

Price per 1,000 Requests: $5

○  Best Use Cases: Quick and cost-effective search tasks requiring
grounded answers, suitable for applications like basic information
retrieval and straightforward question-answering systems.

3.  Sonar Reasoning Pro

○  Company: Perplexity
○  Tier: Pro
○  Model Name: Sonar Reasoning Pro
○  Pricing:

Input Tokens: $2 per million tokens
■
■  Output Tokens: $8 per million tokens
■  Price per 1,000 Requests: $5

○  Best Use Cases: Applications requiring multi-step reasoning and

problem-solving capabilities, such as complex analytical tasks and
decision support systems.

1.  DeepSeek V3

○  Company: DeepSeek
○  Tier: Standard
○  Model Name: DeepSeek-V3
○  Pricing:

■

Input Tokens: $0.07 per million tokens (Cache Hit;
discounted to $0.014 until February 8, 2025), $0.27 per
million tokens (Cache Miss; discounted to $0.14)

■  Output Tokens: $1.10 per million tokens (discounted to

$0.28)

○  Best Use Cases: Conversational AI applications like chatbots and
customer support systems, benefiting from cost-effective token
processing and dynamic response generation.  DeepSeek AI

2.  DeepSeek-R1

○  Company: DeepSeek
○  Tier: Pro
○  Model Name: DeepSeek-R1
○  Pricing:

Input Tokens: $0.14 per million tokens

■
■  Output Tokens: $2.19 per million tokens (includes Chain of

Thought and final answer)

○  Best Use Cases: Tasks requiring logical reasoning and

problem-solving, such as research analysis, legal evaluations, and
strategic decision-making processes.  DeepSeek AI

1.  Grok 2-Vision (XAI)

○  Company: XAI
○  Tier: Pro
○  Model Name: Grok 2-Vision
○  Pricing:

1.  Input: $2 / 1M tokens
2.  Output: $10 / 1M tokens

○  Best Use Cases: Applications integrating visual data processing
with language understanding, such as image captioning, visual
question answering, and multimedia content analysis.

2.  Grok Vision Beta

○  Company: XAI
○  Tier: Standard
○  Model Name: Grok Vision Beta
○  Pricing:

1.  Input: $5 / 1M tokens
2.  Output: $15 / 1M tokens

ii.  Best Use Cases: Grok Vision Beta is best suited for analyzing and

understanding images through tasks like captioning, visual question
answering, and extracting information from screenshots or charts.

●  Tooltips or expandable cards provide additional detail about each model's

capabilities.

●  Pricing and strengths are shown before the user runs the query.

●  Model benefit and cost details update dynamically if new models are added.

Test Scenarios / Cases:

Test Scenario 1: Data updates and source validation

●  Test Case 1: Pricing data is updated in config file → frontend reflects changes

without hardcoding.

●  Test Case 2: Backend returns error or stale data → info panel displays cached

version with warning.

Exception case:

●  Admin uploads malformed info configuration → system logs error, does not

crash, shows "info unavailable" placeholder for that model.

Design: Link to a 1-2 page story technical design document
Estimation: [Story points or time estimate] ⇒ should be within 1 sprint or maximum 2
sprints

Notes:

●  Requires integration with mPass OAuth2 API.

●  Design must comply with single sign-on (SSO) and security best practices.

●  Clarify logout flow — whether logout also triggers mPass logout or just clears

local session.

Owner: [Product Owner]


