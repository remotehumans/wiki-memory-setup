# Follow-up Reminders (Optional)

Set this up only when the user wants reminders about people. Many users will not need it. Describe what the task does; let the user's own agent decide how to schedule it.

## What the wiki already does

People pages carry `last_contact` and `next_touch` (see `AGENTS.md`, People and Follow-ups). Without any scheduled task, the user can ask at any time: "Who do I need to follow up with?"

## Ask the user

1. **Do you want reminders?** If no, stop here.
2. **What should a reminder include?**
   - **Notification only:** names, why, and how overdue.
   - **Draft messages:** the same list, plus a short draft for each person in the user's voice and preferred channel. Drafts are never sent without the user.
3. **How often?** Daily on weekdays is a good default. Weekly suits lighter networks.
4. **Where should it arrive?** In the agent app or by email. Keep reminders out of the wiki folder; they are not knowledge pages.

## The task

Give the scheduler this prompt, filling in the choices:

```text
Open my memory wiki at <path>. Read AGENTS.md.
List people whose next_touch is today or earlier, soonest first.
For each: name, company, why we're following up (from Open Loops), last_contact, channel.
<Notification only: send me that list.>
<Draft messages: also write a short draft for each, in my voice, for their channel. Never send anything.>
Deliver it <in this app / by email to me>.
If nobody is due, say so in one line and name the next person coming up, with their date.
Do not change any wiki pages.
```

When the user later says a follow-up is done, the agent updates `last_contact`, adds a History line and moves or clears `next_touch` as part of normal filing.

## Scheduling options

Use whatever the user's agent supports. Examples, not requirements:

- **Claude desktop (Cowork) or Claude Code:** a scheduled task with the prompt above. Runs while the computer is on.
- **Claude Code in the cloud:** a scheduled routine. Needs the wiki on GitHub.
- **Codex:** an automation with the prompt above.
- **ChatGPT:** a scheduled task, if the wiki is connected (see `storage-and-connectors.md`).
- **A server or always-on computer:** cron running the user's agent CLI with the prompt.

If the agent cannot schedule anything, say so and tell the user they can ask "Who do I need to follow up with?" whenever they like.
