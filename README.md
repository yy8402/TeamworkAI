# TeamworkAI

Supervise AI/LLM to generate a team of AI agents, define the workflow, and get the job done.

I got the idea after watching Andrew NG's [Agentic Reasoning](https://www.youtube.com/watch?v=sal78ACtGTc), and made the conceptual demo with CLI work.   


**Demo**
1. input the task;
2. ask llm to generate a team, make changes if needed;
3. ask llm to define the workflow, make changes if needed;
4. ask llm to simulate the workflow step by step, grading the output of each step and move to the next step only when the output gets a high enough score;
5. send out the final output.


# TODO
1. GUI & web service;
2. support multimodal tasks
3. support more llms, e.g. Gemeni, Claude, LLaMA
4. allow different personas to use different model 
5. compatible with [CrewAI](https://github.com/joaomdmoura/crewAI), which has been doing a great job to get predefined AI crews working on predefined tasks.
6. flowchart for workflow
