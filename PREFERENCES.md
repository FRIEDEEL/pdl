# Documentation Preferences

- Organize the API reference by the actual `src/pdl/` package/module structure.
  Keep complete member documentation at its definition; package re-exports link
  to that location instead of duplicating the reference under topic categories.
- Tutorial prose should explain example code, including its purpose, key calls,
  relevant parameters, and how they produce the visible result. Avoid overly
  terse lessons that provide a few sentences and a code block with little
  explanation. Add detail where it helps understanding, without requiring a
  line-by-line walkthrough. Improve existing lessons gradually under user
  direction rather than rewriting the whole tutorial at once.
- Follow the user's documentation instructions by updating English first and
  synchronizing Chinese in the same work cycle. Keep translated structure,
  content, examples, and limitations mirrored in every commit, including WIP.
- Check manual edits in either language and propagate their intent to the other
  version. Preserve user edits; ask about conflicting or ambiguous changes.
  English-first authoring does not override manual Chinese changes. The generated
  API reference remains English-only, and commits still need explicit approval.
- Keep Chinese and English documentation navigation separate. Each translated
  page links to its counterpart in the other language. Share example sources
  and rendered images; maintain the generated API reference in English only.
- After each round of documentation changes, rebuild the Sphinx HTML site so
  the user can review the updated pages directly in the browser. Report build
  failures and any resulting stale output.
- For examples involving changes, retain the original state as a visual
  comparison reference in the same figure as the changed result. Use a lighter
  color or lower opacity for the original state so readers can directly compare
  what changed. Include meaningful intermediate states when useful; the main
  purpose is comparison, rather than presenting a step-by-step procedure.

# Provisional API and Tutorial Work

- While pdl APIs remain provisional, do not retain old API compatibility unless
  explicitly requested. Update examples and documentation to the current API.
- Name factory functions in lowercase snake_case (for example, `circle`, `text`,
  and `tex`); retain PascalCase for actual classes.
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
- Prefer commit messages with a concise body explaining concrete changes.
  Explicitly mention included test additions or updates, and distinguish them
  from checks that were actually run.

- For the complete architecture refactor on the current branch, the user has
  explicitly delegated local commits again. Keep focused commits with bodies;
  merging into dev, pushing, and release publication remain separate actions.
