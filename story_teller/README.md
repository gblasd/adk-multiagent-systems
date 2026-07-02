# Story Teller Agent

## Overview

The Story Teller Agent is multi-agent system designed for collaborative story writing. This is a simple, yet powerful, multi-agent ADK sample that takes a user prompt and transforms it into a complete, multi-chapter story. The agent leverages a team of specialized AI agents, each with a unique role, to brainstorm, draft, critique, and edit the story, showcasing a sphisticated workflow for creatrive content generation.

## Agent Architecture

This agent uses a sequential workflow that orchestrates several sub-agents to produce a story. The process is as follows:

1. **Prompt Enhancer:** Takes a basic user idea and expands into a detailed premise, setting the stage for the story.
2. **Story Loop:** This is the core of the writing process, which iterates for a predefined number of chapters:
    *   **Paraller Writers:** Whithin the loop, two writer agents, a `Creative Writer` and a `Focused Writer` simultanously create two different versions of the next chapter. The `Creative Writer` uses a high temperature for more imaginative and unpredictable results, while the `Focused Writer` uses a low temperature for more logical and consistent writing.
    *   **Critique Agent:** This agent reviews the two chapter draft and selects the one that best fits the story's premise and narrative arc.
3. **Edit Agent:** Once all chapeters are written, the `Edito Agent` performs a final review of the entire story, polishing it for a grammar, flow, and consistensy.

:::mermaid
flowchart TD
    %% Nodes
    user_prompt["User Prompt"]
    prompt_enhancer("Prompt Enhancer Agent")
    story_loop{"Story Loop"}
    parallel_writers["Parallel Writers"]
    creative_writer("Creative Writer")
    focused_writer("Focused Writer")
    critique_agent{"Critique Agent"}
    editor_agent("Editor Agent")
    final_story["Final Story"]

    %% Connections
    user_prompt --> prompt_enhancer
    prompt_enhancer --> story_loop
    
    story_loop --> parallel_writers
    story_loop --> editor_agent
    
    parallel_writers --> creative_writer
    parallel_writers --> focused_writer
    
    creative_writer --> critique_agent
    focused_writer --> critique_agent
    
    critique_agent --> story_loop
    editor_agent --> final_story

    %% Styling Theme
    classDef default fill:#E8E5FF,stroke:#8A76F7,stroke-width:1.5px,color:#1A1A1A;
    linkStyle default stroke:#1A1A1A,stroke-width:2px;
:::