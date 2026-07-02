from google.adk.agents import (
    LlmAgent,
    LoopAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.genai import types

from . import intructions

# --- Configurations constants ---
APP_NAME = "collaborative_story_writer"
MODEL_NAME = "gemini-2.5-flash"

# User-Defined Constraints
N_CHAPTERS = 3 # Number of chapters to write
MAX_WORDS = 100 # Max words per chapter

# --- State Keys ---
KEY_USER_PROMPT = "user_prompt"
KEY_ENHANCED_PROMPT = "enhanced_prompt"
KEY_CURRENT_STORY = "current_story"
KEY_CREATIVE_CANDIDATE = "creative_chapter_candidate"
KEY_FOCUSED_CANDIDATE = "focused_chapter_candidate"
KEY_FINAL_STORY = "final_story"

def set_initial_story(callback_context, llm_request):
    callback_context.state[KEY_CURRENT_STORY] = "Chapter 1"

# --- 1. Agent Definitions ---

# Expands the user's simple idea into a full premise
prompt_enhancer = LlmAgent(
    name="PromptEnhancerAgent",
    model=MODEL_NAME,
    description="Expands user prompt into a fall story premise",
    instruction=intructions.PROMPT_ENHANCER_INSTRUCTION,
    output_key=KEY_ENHANCED_PROMPT,
    before_model_callback=set_initial_story
)

# Focuses on novelty and twists (High Temperature)
creative_writer = LlmAgent(
    name="CreativeStoryTellerAgent",
    model=MODEL_NAME,
    # High temperature for creativity/randomness
    generate_content_config=types.GenerateContentConfig(temperature=0.9),
    instruction=intructions.CREATIVE_WRITER_INSTRUCTION.format(
        max_words=MAX_WORDS
    ),
    description="Writes a creative, high-temperature chapter draft.",
    output_key=KEY_CREATIVE_CANDIDATE
)

# Focuses on logic and consistency (Low Temperature)
focused_writer = LlmAgent(
    name="FocusedStoryTellerAgent",
    model=MODEL_NAME,
    # Low temperature for consistency/logic
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    instruction=intructions.FOCUSED_WRITER_INSTRUCTION.format(max_words=MAX_WORDS),
    description="Writes a consistent, low-temperature chapter draft",
    output_key=KEY_FOCUSED_CANDIDATE,
)

# Selects the best chapter and append it to the story
# Notice: This agent reads the current story AND the candidate, then outputs the UPDATED full story.
critique_agent = LlmAgent(
    name="EditorAgent",
    model=MODEL_NAME,
    instruction=intructions.CRITIQUE_AGENT_INSTRUCTION,
    description="Selects the best chapter and updates the story state.",
    output_key=KEY_CURRENT_STORY, # overwrites current_story with the extended version
)

# Final Polish
editor_agent = LlmAgent(
    name="EditorAgent",
    model=MODEL_NAME,
    instruction=intructions.EDITOR_AGENT_INSTRUCTION,
    description="Polishes the final draft.",
    output_key=KEY_FINAL_STORY
)

### --- 2. Workflow Structure ---

# Runs the creative and Focused writers at the same time
parallel_writers = ParallelAgent(
    name="ParallelChapterGenerators",
    sub_agents=[creative_writer, focused_writer],
    description="Generates two chapter options in parallel."
)

# This sequence runs inside the loop (Generate -> Critique/Append)
chapter_cycle = SequentialAgent(
    name="ChapterGenerationCycle",
    sub_agents=[parallel_writers, critique_agent],
    description="Runs parallel writers then selects the best chapter",
)

# Repeats the Chapter N times.
story_loop = LoopAgent(
    name="StoryBuildingLoop",
    sub_agents=[chapter_cycle],
    max_iterations=N_CHAPTERS,
    description=f"interatively writer {N_CHAPTERS} chapters"
)

# Enhance Prompt -> loop Chapters -> Final Edit
root_agent = SequentialAgent(
    name="CollaborativeStoryWorkflow",
    sub_agents=[prompt_enhancer, story_loop, editor_agent],
    description="End-to-end story generation pipeline."
)