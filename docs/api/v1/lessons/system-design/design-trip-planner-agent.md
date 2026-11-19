# Design a Trip Planner Agent

> A travel site wants a chat assistant that answers trip questions using its own data: which hotels match, how far they are from the sights, what's nearby. Design the agent.

- Track: System Design › Agents › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-trip-planner-agent/
- Before this: Tool and Function Calling (`ai-engineering/tool-calling`), What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A travel site has millions of listings, reviews, live prices and maps. It wants a chat assistant that answers questions like "is this hotel walkable to the station?" and helps plan trips. The interviewer asks:

> A travel site wants a chat assistant that answers trip questions using its own data: which hotels match, how far they are from the sights, what's nearby. Design the agent.

#### Ask before designing

- **Questions:** "is this hotel walkable to the station?", "which of these has a pool?", "plan three days in this city with kids".

- **Data:** listings, reviews, availability and prices, maps and transport.

- **Scope:** answers and suggestions now; later, booking and changing trips.

- **Must never happen:** wrong prices or availability, invented amenities, or booking without the user's clear confirmation.

- **Success metrics:** answer accuracy, conversion to booking, latency, and cost per conversation.

### The idea

Think of a hotel concierge. First they work out exactly which place you mean. Then they check the live booking system and a map, not their memory, and they never book anything without asking you first.

[Figure: A small model classifies the request. Places are matched to real listing IDs. The agent chooses tools for live data. A large model writes a grounded answer.]

_Match the place first; get every fact from a tool._

### Play

**Try to break it.** Slide the share of steps handled by small models from 0 to 80%.

#### Route each step to the right model

Illustrative: 6 steps per conversation; a large-model step costs 1 cent and takes 2 s, a small one 0.05 cents and 0.2 s. Real prices vary.

Slide it up. Classification, extraction and entity matching are narrow tasks a small, tuned model does well; keep the large model for planning and the final answer, where quality is visible to the user.

**Now say why:** which steps can a small model handle, and which need a large one?

## Architecture

### Architecture

#### In one breath

The agent decides which tools to call instead of following a fixed script. Step one is always **entity matching**: turn "that hotel near the old town" into a real listing ID. Then call tools for listing data, availability, prices, and distances and travel times. Use **small, travel-specific models** for fast routine steps and a **large model** for reasoning and the final answer. Every fact comes from a tool, never from the model's memory. Bookings, later, need explicit user confirmation.

#### Match, choose tools, ground, answer

1. **Classify:** a small model labels the request (question about a listing, planning, support) and extracts dates, places and filters.

2. **Match entities:** map each place or hotel mentioned to its ID, using search plus the conversation so far; ask when it's ambiguous.

3. **Pick tools:** the agent chooses among listing details, reviews, availability and prices, recommendations, and distance and travel-time tools.

4. **Ground:** tool results go into the context with their source; the answer may use only those facts.

5. **Answer:** a large model writes the reply, with links to the listings.

##### A platform, not one agent

Shared infrastructure lets many teams build agents by configuration: common tools, evaluation and deployment. The trip planner is the first agent on it; support, cross-selling and trip changes come next.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Conversations a day | given | **1 million** |
| Tool calls a day | 1 million × 5 | **5 million** |
| Peak tool calls a second | 5 million ÷ 86,400 × 3 | **about 175** |
| LLM cost a day | 1 million × 1.4 cents | **about $14,000** |

Prices and availability change by the minute, so they're always fetched live; static listing details can be cached.

## In practice

### In practice

#### What every travel agent design gets asked

- **Entity matching:** the hardest early step. Use the conversation context, the user's search, and location; when two hotels share a name, ask.

- **Tools and permissions:** read-only tools for answers. Booking tools need the user's explicit confirmation of dates, price and cancellation terms, and must be safe to retry.

- **Planning and memory:** keep the trip's dates, party and preferences in session memory; long-term memory of past trips needs consent.

- **When to stop:** a step budget per turn; if a tool fails or data is missing, say so instead of guessing.

- **Specialised versus general agents:** many narrow agents are easier to test; fewer general ones are easier to run. Teams are still finding the balance.

- **Evaluation:** a test set of real questions with checkable facts (distances, amenities); check every number in an answer against the tool output.

#### What the real system reported

- **The agent:** matches properties mentioned by users to the right IDs, fetches data from internal systems, and computes distances and travel times to landmarks and transport; it replaced a fixed flow, so the agent now decides which systems to call.

- **The platform:** configuration-driven agents on shared infrastructure, with multi-agent work, multimodal input and long-term memory planned.

- **Models:** small travel-specific models for fast, cheap inference and larger models for reasoning; the company reported doubled accuracy on retrieval, ranking and customer tasks, and 1.5 to 1.7 times more human agent capacity.

From trade-press reports and a podcast summary (2025). The figures are self-reported.

### The answer that sounds right

#### "A big model already knows the hotels"

It sounds plausible, but a model's memory is out of date and can't know today's prices or availability. It will invent amenities and distances. Match the listing, fetch facts from tools, and answer only from those.

## Say it

### A travel site wants a chat assistant that answers trip questions using its own data: which hotels match, how far they are from the sights, what's nearby. Design the agent.

#### The interviewer pushes further

Follow-up 1 of 3

Why match entities before anything else?

Every tool needs an ID. If "the hotel by the river" maps to the wrong listing, every later fact is about the wrong place, however good the model is.

Follow-up 2 of 3

The agent quoted a price that had changed. How do you prevent it?

Never cache prices or availability; fetch them live when answering, show when they were fetched, and re-check before any booking.

Follow-up 3 of 3

Why not use the largest model for every step?

Cost and latency multiply by the number of steps. Narrow steps like classification and matching work well with small tuned models, so save the large model for reasoning and the reply.

I'd clarify the kinds of questions, the data, whether we book or only advise, and latency and cost targets. A small model classifies each request and extracts dates, places and filters. Then entity matching maps every hotel or place mentioned to a real ID, asking when it's ambiguous. The agent chooses tools: listing details, reviews, live availability and prices, and distance and travel time. All facts come from tool results, and the answer may only use those. Routine steps run on small tuned models; planning and the final reply use a large model, which cuts cost and latency a lot. Session memory holds the trip details. Booking, later, needs explicit confirmation and retry-safe tools. I'd evaluate with real questions whose facts can be checked against tools.

**Key terms and sources**

Based on a travel company's published work, reported by the trade press: an internal platform for modular agents and a podcast summary on small and large models (Dec 2025). The company's own post couldn't be fetched, so details come from these reports. The lab is illustrative; the estimate is ours. Uses tool calling, what an agent is and grounded answers.
