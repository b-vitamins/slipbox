# Agent Development Guidelines

These guidelines describe how automated or human contributors should work on this
repository.

## Commit Message Standards
- Use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
  style for all commits.
  - Examples: `feat: add new note about quantum theory`,
    `fix: correct typo in README`, `chore: update dependencies`.
- Keep commits small and focused. Each commit should contain a logical unit of
  work.

## Pull Request Standards
- Title should follow Conventional Commit format summarizing the change.
- Provide a clear description of what was done and why.
- Include testing instructions when relevant.

## Code Housekeeping
- Run `shellcheck` on all shell scripts before committing.
- When modifying `setup-dev.sh`, execute it once to ensure it completes without
  errors.
- Update documentation when behavior or usage changes.

## Version Management
- This repository does not currently publish releases, but if version tags are
  added they should follow [Semantic Versioning](https://semver.org/).

## CHANGELOG
- Major updates should be recorded in `CHANGELOG.md` with sections `Added`,
  `Changed`, `Fixed`, etc.

## Testing
- If scripts are modified, run them in a clean environment when possible.
- For this repository, there are no automated tests; manual verification is
  sufficient.

