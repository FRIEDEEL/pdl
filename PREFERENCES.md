# Documentation Preferences

- For examples involving changes, retain the original state as a visual
  comparison reference in the same figure as the changed result. Use a lighter
  color or lower opacity for the original state so readers can directly compare
  what changed. Include meaningful intermediate states when useful; the main
  purpose is comparison, rather than presenting a step-by-step procedure.

# Provisional API and Tutorial Work

- While pdl APIs remain provisional, do not retain old API compatibility unless
  explicitly requested. Update examples and documentation to the current API.
- During this development stage, prioritize clear behavior descriptions and
  understandable examples over polished tutorial prose and smooth transitions.
- Organize tutorials into a few major parts; teach Group, Gather, and Layer
  before reference points and Frame within organization and positioning.

# Design Discussions

- `DEVLOG.md` is written by the user or edited under the user's explicit
  direction. Do not automatically append conversations, implementation progress,
  decisions, or test reports. Write only the content the user asks to record.
- Use `refactor_note.md` as temporary discussion guidance on the current
  refactor branch. Check new proposals against confirmed decisions and
  distinguish user decisions, assistant suggestions, and unresolved questions.
  Consolidating the note into `DEVLOG.md` also requires explicit user direction.

# Git Review

- Unless the user explicitly delegates committing, present each proposed commit
  for review and wait for explicit approval before execution. Implementation
  authorization does not imply commit authorization.
- Provide the proposed commit message, file scope, concise change summary,
  validation results, and known incomplete work. Keep unrelated user edits out.
- Previous autonomous commit and merge authorization is revoked. Obtain explicit
  merge approval separately from approval of individual commits.
