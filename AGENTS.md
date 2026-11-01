# Working Agreements

## Communication and Change Authorization

- Discuss work with the user in Chinese. Write this file in English.
- The AI owns implementation, routine design choices, testing, documentation,
  and local Git integration within the agreed project goals. Do not request
  separate approval for each implementation step, commit, or feature merge.
- The user performs acceptance between stages, reviewing architecture, example
  code, and rendered results. Once stage goals are agreed, handle internal
  design and implementation decisions autonomously rather than introducing
  additional approval checkpoints within the stage.
- Explain significant approaches and trade-offs concisely. Ask before changes
  that materially exceed the agreed stage scope; report decisions and concrete
  examples and outputs at the stage acceptance checkpoint.
- Read relevant files and inspect the project as needed to prepare a proposal.
- Report what changed, which checks were run, and any unresolved issues.

## Language

- Keep English as the primary language for reader-facing documentation, with
  corresponding Chinese translations derived from the English versions. Use
  `README_zh.md` for the Chinese README; the main README is English.
- Use English for code comments, docstrings, commit messages, and this file.
  `DEVLOG.md` remains Chinese as described below.
- Write `DEVLOG.md` in Chinese during the current solo development stage.
  Plan to transition it to English if the project adopts a collaborative
  workflow; agree on the timing and translation scope with the user first.
- Continue discussing work with the user in Chinese.

## Python Project Conventions

- Use pyenv to manage Python versions.
- Use uv to manage projects, virtual environments, and dependencies.
- Use the Python interpreter selected through pyenv for the project's virtual
  environment.
- Run project commands through `uv run`.
- Initialize new Python library projects with `uv init --library` and use a
  `src/` layout.
- Follow the existing structure in established projects. Do not migrate
  project layouts without explicit instructions.

## File Organization

- Organize implementation modules into responsibility-based packages under
  `src/pdl/`; keep only package initialization and typing markers at its root.
- Group example sources by topic, with only a few examples per directory.
- Mirror package module paths under `tests/unit/`, retaining `test_<module>.py`
  filenames. Integration tests are organized by the external workflow.
- Mirror example source directories under `examples/output/`: for example,
  `examples/text/labels.py` writes `examples/output/text/labels.svg` and related
  formats. Keep generated outputs out of Git.

## Dependency Management

- Before adding a dependency, explain its purpose and whether it is needed at
  runtime or only for development, as part of the proposed change.
- Keep runtime dependencies minimal and place development tools in development
  dependency groups.
- Use uv to update dependency declarations and `uv.lock`, keeping them consistent.
- Do not upgrade unrelated dependencies as a side effect of other work.

## Testing

- Use pytest. Put unit tests under `tests/unit/` and external-tool integration
  tests under `tests/integration/`.
- By default, mirror the package's module structure in the unit test directory,
  naming test files `test_<module>.py`.
- For example, `src/package_name/io/reader.py` corresponds to
  `tests/unit/io/test_reader.py`.
- Run relevant tests after changes and report the results.
- Prioritize public behavior, edge cases, and regression coverage for fixed bugs.
- Avoid tests that merely repeat implementation logic or depend unnecessarily
  on internal details.
- Distinguish numerical and structural tests from image comparison tests for
  drawing features. Agree on the rendering test strategy once the drawing
  approach is defined.

## Code Quality and Type Checking

- Use Ruff for linting and formatting.
- Use Pyright for static type checking with `typeCheckingMode = "strict"`.
- Keep tool configuration in `pyproject.toml`.
- Add type annotations to function parameters and return values, including
  `-> None` where appropriate.
- Avoid unnecessary `Any` annotations. Keep necessary type-checking
  suppressions narrowly scoped and explain why they are needed.
- Write all comments and docstrings in English.
- Use Google-style docstrings with `Args`, `Returns`, and other sections where
  applicable. Follow this general format:

  ```python
  def normalize(value: float, scale: float) -> float:
      """Normalize a value by the given scale.

      Args:
          value (float): The value to normalize.
          scale (float): The nonzero normalization scale.

      Returns:
          float: The normalized value.
      """
      return value / scale
  ```

- Run the following checks after relevant changes:

  ```sh
  uv run ruff check .
  uv run ruff format --check .
  uv run pyright
  uv run pytest
  ```

## Reader Documentation

- Use Sphinx with MyST for the documentation site, autodoc for public API
  signatures/docstrings, and Napoleon for Google-style docstrings.
- Maintain English tutorials under `docs/tutorial/en/` and corresponding Chinese
  versions under `docs/tutorial/zh/`. The shared API reference uses English
  source docstrings; do not present it as a translated Chinese reference.
- Teach drawing step by step, introducing only a few new concepts per example.
  Use Manim Community tutorials for teaching rhythm and the PGF/TikZ manual
  for graphical explanations and terminology. Do not imply unsupported TikZ
  syntax or features are available in pdl.
- Pair each tutorial step with runnable source under `examples/tutorial/` and
  its actual rendered output. Use axes, guide lines, control points, or
  before/after comparisons when they help explain the current topic.
- Explain file saving in Hello world. Later body snippets show drawing code
  only; keep path handling and export plumbing in the linked full examples.
  Include source with `literalinclude` rather than maintaining copied snippets.
- Introduce common drawing operations before rendering internals. Teach basic
  Path construction before advanced subpaths, fill rules, and backend lowering.
- Document units, coordinate meanings, defaults, mutation/capture behavior, and
  material limitations in API docstrings, with short examples where useful.
- Build with `uv run --group docs sphinx-build -W --keep-going -b html docs
  docs/_build/html`. The build generates tutorial images; inspect the actual
  output as well as checking build warnings. Keep generated artifacts out of Git.

## Development Log

- `DEVLOG.md` is user-authored. Edit it only when the user explicitly directs
  what to write or change, and stay within that scope. Do not automatically add
  discussions, implementation progress, decisions, or validation results.
- Keep the formal log concise. Record durable conclusions and meaningful
  milestones rather than chat transcripts, temporary task status, or repetitive
  validation reports.
- Organize content by topic as needed. No fixed set of sections is required.
- Use Mermaid diagrams, including class diagrams and flowcharts, when they
  help explain the discussion.
- When adding dated notes, place them under `Dated Note` with headings in
  the format `### YYYY-MM-DD HH:mm:ss`, using local time (Asia/Tokyo).
- Keep all dated notes in reverse chronological order, newest first. Sort by
  the full timestamp, including times within the same day, and insert each new
  entry at its correct position rather than appending it at the bottom.
- Distinguish tentative ideas from agreed decisions.
- Preserve useful dated history and record subsequent changes in new entries;
  remove or rewrite historical entries only when the user authorizes cleanup.
- Use `refactor_note.md` as temporary guidance for the current refactor branch.
  At branch completion, consolidate confirmed decisions and branch outcomes into
  `DEVLOG.md` only under the user's explicit direction, and update the relevant
  architecture documentation before removing the temporary note. Do not treat
  the note as implementation authorization.

## Changelog

- Use `CHANGELOG.md` to document user-facing changes by release.
- Collect pending release notes under `Unreleased`.
- On release, organize those notes under the version number and release date.
- Describe notable additions, behavior changes, deprecations, removals,
  and fixes. Clearly identify breaking changes and migration steps.
- Summarize changes from the user's perspective rather than copying commit
  messages or internal design discussions.

## Git Workflow

- Use Gitflow as a baseline, with flexibility for solo development.
- Use `main` for released code and `dev` for development integration.
- Direct development on `dev` is allowed, especially during initial
  scaffolding and MVP development. Do not create a feature branch for every task.
- When a feature branch is used, use `feat/*`, branching from and merging
  back into `dev`.
- Use `feat/*` for bounded feature work after initial scaffolding; keep related
  changes on the branch and integrate after the relevant checks pass.
- Use `release/*` branches for release preparation, branching from `dev`
  and merging into both `main` and `dev` when the release is complete.
- Use `hotfix/*` branches for urgent fixes to released code, branching from
  `main` and integrating the fixes into both `main` and `dev`.

### Commit Messages

- Write all commit messages in English, including subjects, bodies, and footers.
- Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
- Use the format `<type>[optional scope][optional !]: <description>`, with a
  short description and optional body and footers separated by blank lines.
- Scopes are optional. Include one when it helps readers understand the area
  affected by the change; omit it when the description is already clear.
- Choose scopes by meaning rather than mechanically mapping them to files or
  directories. For example, `docs(AGENTS)` can clarify a change to working
  agreements without establishing a general file-based scope convention.
- Let scope conventions emerge as the project evolves. Reuse established
  scopes for the same concepts, consulting recent commit history when helpful.
  Introduce a new scope when it improves clarity; no exhaustive scope list
  is required upfront.
- Use `feat` for new features and `fix` for bug fixes. Other types include
  `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, and `revert`.
- Use lowercase type names consistently.
- Use the additional `wip` type for incomplete development checkpoints, such as
  `wip(renderer): sketch the drawing pipeline`. Describe remaining work and
  known failing checks in the body when applicable.
- Mark breaking changes with `!` before the colon or a `BREAKING CHANGE:`
  footer, and explain the incompatible change.
- Apply this format to merge commits as well, for example:
  `chore(merge): integrate feat/rendering into dev`.

### Commit Granularity

- Prefer small, focused commits that capture a clear development step.
- A single function, class method, or localized change may justify a commit.
- WIP commits are acceptable. Clearly indicate their incomplete status
  in the commit message.
- Do not combine unrelated changes merely to produce a larger commit.

### Validation and Integration

- WIP commits may temporarily fail checks. Clearly report incomplete work and
  known failing checks when creating them.
- Before merging into `dev`, ensure that the relevant lint, formatting,
  type-checking, and test checks pass on the resulting combined code.
- When developing directly on `dev`, require relevant checks to pass at
  the end of a completed work phase rather than before every small commit.
- Do not describe work as complete while relevant checks remain failing or
  unverified. Report any blockers explicitly.

### History and Merging

- Preserve the complete development history, including fine-grained and
  WIP commits.
- Use merge as the default integration method. Always use `git merge --no-ff`
  when merging branches.
- Do not rebase, squash, amend commits, or otherwise rewrite existing history
  unless explicitly instructed.
- The user has granted standing authorization to create branches, make commits,
  and merge completed feature work into `dev` for authorized project work.
  Commit each feature or focused development step separately, follow the
  message and granularity rules above, and use `git merge --no-ff`.
- This standing authorization does not include push or release publication.
  Perform those actions only when explicitly instructed.

## Architecture Boundaries

- Before each new design proposal, consult `refactor_note.md` while it exists,
  along with relevant confirmed decisions in `DEVLOG.md`. Reference decision IDs
  where available and report whether the proposal is compatible, a compatible
  extension, conflicting, or insufficiently defined.
  Keep confirmed decisions, pending suggestions, rejected alternatives, and the
  current implementation distinct. Do not promote an assistant suggestion to a
  decision without explicit user confirmation or silently replace prior decisions.
- Treat the architecture in this section and `docs/architecture.md` as mandatory
  implementation constraints. Read the architecture document before designing
  or changing implementation, and identify the owning module and allowed
  dependencies before adding a feature.
- Implement new functionality within these boundaries. Do not work around them
  with function-local imports, dynamic imports, hidden state, duplicate object
  models, or backend-specific exceptions to Author semantics.
- If a requirement cannot be met within the agreed architecture, explain the
  concrete conflict, alternatives, and affected boundaries before implementation.
  Obtain explicit user approval for an architecture change; ordinary feature
  authorization does not authorize silently changing the architecture.
- During review, verify responsibilities and dependency direction as well as
  behavior. Passing tests alone does not establish architectural compliance.
- Author is the sole drawing object model. Do not introduce a parallel Resolved
  scene hierarchy. Anchors and placement inputs are evaluated immediately from
  the referenced object's current state; later edits do not create live bindings.
- Keep numerical geometry and typography measurement in `foundation/`, with no
  dependency on Author, Canvas, backends, or extensions.
- Keep editable 2D drawing semantics in `author/`. It may use foundation services,
  including external TeX measurement, but must not import output adapters.
- Place 3D and advanced diagram components under `extensions/`; core 2D must not
  depend on these extensions. Capture expands extensions into core descriptions.
- Canvas owns submissions, ordering, and viewport policy. Backends consume the
  narrow `canvas.records.Page` contract, never the Canvas implementation.
- Implement anchors numerically in pdl; do not delegate placement to TikZ anchor
  syntax or native diagram-node layout. Backend primitive optimizations must
  preserve the already defined geometry and placement.
- See `docs/architecture.md` and run the architecture boundary tests with the
  normal validation suite when moving code or introducing dependencies.
