# Working Agreements

## Communication and Change Authorization

- Discuss work with the user in Chinese. Write this file in English.
- Before modifying code, explain the proposed approach and its reasoning,
  using only the minimum code snippets needed to make the proposal clear.
- Wait for explicit authorization before modifying code. If the user has
  already explicitly authorized the proposed changes, proceed within that scope.
- Read relevant files and inspect the project as needed to prepare a proposal.
- Report what changed, which checks were run, and any unresolved issues.

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

## Testing

- Use pytest for testing and place tests in `tests/`.
- By default, mirror the package's module structure in the unit test directory,
  naming test files `test_<module>.py`.
- For example, `src/package_name/io/reader.py` corresponds to
  `tests/io/test_reader.py`.
- Run relevant tests after changes and report the results.

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

## Development Log

- Use `DEVLOG.md` to record project motivation, ideas, design discussions,
  decisions, and open questions.
- Organize content by topic as needed. No fixed set of sections is required.
- Use Mermaid diagrams, including class diagrams and flowcharts, when they
  help explain the discussion.
- When adding dated notes, place them under `Dated Note` with headings in
  the format `### YYYY-MM-DD HH:mm:ss`, using local time.
- Distinguish tentative ideas from agreed decisions.
- Preserve dated history and record subsequent changes in new entries.

## Changelog

- Use `CHANGELOG.md` to document user-facing changes by release.
- Collect pending release notes under `Unreleased`.
- On release, organize those notes under the version number and release date.
- Describe notable additions, behavior changes, deprecations, removals,
  and fixes. Clearly identify breaking changes and migration steps.
- Summarize changes from the user's perspective rather than copying commit
  messages or internal design discussions.

## Git Workflow

- Follow Gitflow.
- Use `main` for released code and `develop` for development integration.
- Use `feature/*` branches for feature development, branching from and merging
  back into `develop`.
- Use `release/*` branches for release preparation, branching from `develop`
  and merging into both `main` and `develop` when the release is complete.
- Use `hotfix/*` branches for urgent fixes to released code, branching from
  `main` and integrating the fixes into both `main` and `develop`.
- Do not treat authorization to edit files as authorization to commit, push,
  merge, or publish a release. Perform these actions only when explicitly
  instructed.
