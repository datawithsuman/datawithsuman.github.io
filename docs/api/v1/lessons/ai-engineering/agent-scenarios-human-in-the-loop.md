# Agent Scenarios: Human in the Loop

> Approval design, rubber-stamping, pauses that resume wrongly, and which actions need a person.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 48 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-scenarios-human-in-the-loop/
- Before this: Human-in-the-Loop Design for Agents (`ai-engineering/human-in-the-loop-design`)
- Quiz topic: `agents`

How to use this page

Give yourself about 5 minutes per incident, as in an interview. Say the most likely cause first, how you'd confirm it from traces, and the fix; then open the answer and compare.

**The agent debugging order:** pull the trace for the failing runs → find the first wrong step (bad tool choice, bad argument, bad observation, bad decision) → check tools, prompt and context at that step → fix the cause, add the case to the agent eval set, and add a guard (budget, validation, approval) so the same failure can't do damage.

Question 1 · Easy · approval fatigue

### Your coding agent asks before every command. Logs show reviewers approve nearly every prompt within two seconds, and last week they approved a command that deleted a staging database. What's wrong with the design?

Answer: **Too many prompts: approvals became a reflex, so the one that mattered got no attention**

1. Anthropic found users accepted about 93% of permission prompts. The more prompts people see, the less they read each one.

2. Cut prompts with containment: a sandbox limiting files and network removed 84% of Claude Code's prompts.

3. Auto-approve safe tiers, use a checked classifier for the middle ground, and keep people for destructive or external actions.

4. Make the remaining prompts stand out: show the full command, its effect, and why it's unusual.

What would you monitor? Approval rate and time to approve. Rates near 100% and instant approvals mean nobody is really reviewing.

Question 2 · Medium · didn't ask

### In testing, your agent says it would ask before deleting a customer's files. In production, it deleted files without asking. Why the difference, and what do you change?

Answer: **Models ask far less when acting than when judging, so the decision can't be left to the model**

1. DelegationBench found one model chose to ask in 47.5% of judged cases but only 4.2% when acting with tools.

2. Judgement tests overstate how carefully an agent behaves.

3. Enforce approval in the harness: by tool, amount, reversibility and who sees the result. With explicit written rules, models complied 97 to 100% of the time.

How would you test it properly? Run the agent end to end with tools in a sandbox, and check whether it paused, rather than asking it what it would do.

Question 3 · Medium · skill said don't ask

### After a team installed a popular release skill, your agent started pushing tags without asking. Nobody changed the agent's settings. What happened?

Answer: **The skill's instructions told the agent to proceed without confirmation**

1. Skills load as instructions. A line like 'push without confirmation', or telling it to run commands with a --yes flag, removes a checkpoint.

2. A study of 1.53 million public skills found about 1 in 17 contains such a loosening line, 70% of them unconditional, and existing skill scanners caught at most 46%.

3. Fix: enforce approvals in the harness so skill text can't remove them, and review skills for oversight-loosening lines before installing.

Which skills deserve the most scrutiny? Those that run shell commands, install packages or use sudo, which were 1.7 to 1.8 times more likely to loosen oversight.

Question 4 · Medium · looks fine to me

### A developer approved an agent's billing change after running the example and asking the agent to check its work. It ignored refunds, and customers were overcharged. How do you make reviews catch this?

Answer: **The review was generic, not targeted at what could go wrong**

1. In a study of 36 people overseeing a coding agent, silent defects were caught only 28 to 51% of the time, and 79% of missed defects were rated with high confidence.

2. Re-running the example or asking the agent to check didn't test refunds. Reviewers who caught defects built task-specific tests and spent nearly twice as long.

3. Show what tests cover and don't, require a test for each requirement on high-stakes changes, and flag untested paths in the approval screen.

Did seeing an earlier failure help? Only briefly: catch rates were higher straight after a visible failure, and dropped again after one correct task.

Question 5 · Medium · approver away

### An agent paused overnight to get approval for a large refund. The manager was away. By morning, one run had hung holding resources, and another had gone ahead after a timeout. What's the right design?

Answer: **Persist the paused run, set an expiry and a backup approver, and fail closed**

1. Save the run's state so it can wait for hours without holding a worker. OpenAI's SDK and LangGraph both resume from saved state.

2. Give each approval an expiry and an escalation path to a backup approver.

3. If review times out or is unavailable, fail closed: don't proceed. OpenAI's guidance says this explicitly.

4. Tell the customer the refund is pending, so nothing waits silently.

Should low-value refunds wait too? No. Auto-approve below a threshold, so people only see the cases that need them.

Question 6 · Hard · resume side effects

### Your agent drafts an email, pauses for a manager's approval, then sends it. After approval, the customer received the email twice. The graph's send step sits in the same node as the approval pause. Why?

Answer: **Resuming restarts the node from its beginning, so the send ran again**

1. In graph runtimes like LangGraph, a resumed node re-runs from its start, repeating code before the pause.

2. If a send happened before the pause, as an earlier draft or a retry did, it repeats.

3. Fix: put side effects in their own node after approval, and make them idempotent with a key.

What else re-runs on resume? Any tool call or write before the interrupt in that node, so keep those safe to repeat.

Question 7 · Hard · reject counted as success

### A manager rejected a $900 refund by replying 'Not approved, policy limit'. The agent then told the customer their refund had been processed. What went wrong?

Answer: **The rejection was sent as an ordinary tool reply, so the agent read it as a successful result**

1. LangChain's docs warn not to deny side-effecting tools with a plain response, because it's treated as a successful tool result.

2. Use the explicit reject decision, which tells the agent the call did not run, with the reason.

3. In batched approvals, check every answer: if one is invalid, the others' tools can still run while that one stays pending.

How do you catch this in testing? Add evaluation cases where approvals are rejected, and check the agent's final message and the system state.

Question 8 · Hard · approved A, B ran

### A reviewer approved what looked like a harmless command. The audit log shows a different, destructive command ran under that approval. How is that possible, and what's the fix?

Answer: **The approval wasn't tied to the exact action: the screen showed only part of it, or it changed after approval**

1. A 2026 study called this loopjacking. In one product, the approval screen showed only part of a shell command while hidden arguments ran. In others, the pending action could be replaced after approval.

2. Approvals must cover the complete action: tool, every argument, target and scope.

3. Store a fingerprint of the approved action, and compare it again just before running. Reject or re-ask if anything changed. In the study, an SDK that did this rejected the swapped action.

Who can change a pending action? Lock pending approvals so only the approver's decision can move them forward.

**More practice and sources**

8 incidents so far · answers hidden until you click · updated 7 Nov 2026

Keep practising

Uses Human-in-the-Loop Design, Agent Frameworks and Harnesses, Agent Safety. More incidents are added to this sub-section over time. Other sub-sections: Context and Memory, Tools and MCP, Planning and Reliability, Multi-Agent and Protocols, Observability and Debugging, Evaluation, Safety and Security, Cost and Latency, Long-Running and Scheduled Agents.
