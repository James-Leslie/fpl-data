# Summary
`fpl-data` is a Python package for loading and transforming data from the Fantasy Premier Leage API.

# Tooling
- Package management: `uv` (strictly no pip/conda)
- CI/CD: GitHub Actions
- Distribution: PyPI
- Testing: pytest

# Development environment
- Package structure: `src/fpl_data/`
- Configuration in `pyproject.toml`
- Dependencies managed via `uv.lock`
- Tests in `test/` directory

# Code standards and preferences
## Python style
- Use type hints for all functions and methods
- Use f-strings for string formatting
- Follow PEP 8 guidelines for code style
- Write docstrings using Google style

## UV commands (never use pip/conda)
```bash
# Dependency management
uv add package-name              # Add runtime dependency
uv add --dev package-name        # Add development dependency
uv remove package-name           # Remove dependency
uv sync                          # Sync environment with lockfile

# Execution
uv run script.py                 # Run Python scripts
uv run pytest                    # Run tests with pytest

# Version management
uv version --bump patch          # Bump patch version
uv version --bump minor          # Bump minor version
uv version --bump major          # Bump major version
```

## Package Management Rules
- **ALWAYS use `uv add` and `uv remove` commands for dependency management**
- **NEVER manually edit pyproject.toml [dependency-groups] or [project.dependencies] sections**
- Let UV handle version resolution and lockfile updates automatically
- UV will update `pyproject.toml` and `uv.lock` automatically when adding/removing packages

## Testing
- Use `pytest` for testing
- Write tests in the `test/` directory
- Aim for high test coverage
- Run tests with `uv run pytest`
- Test files should mirror source structure
- Use fixtures for common test data

## Documentation
- `README.md` should include:
  - Clear project description
  - Installation instructions (uv and pip)
  - Basic usage examples
  - Contributing guidelines
  - License information
- Code should be self-documenting with clear variable names
- Complex algorithms need inline comments
- Public APIs need comprehensive docstrings

## GitHub Integration
- Use GitHub CLI
- Use conventional commits when possible
- Create meaningful release notes
- Tag releases with semantic versioning (v1.0.0)
- Let GitHub Actions handle PyPI publishing
- Never commit sensitive information (API keys, tokens)

## Commit Guidelines
- **Make regular, frequent commits** - commit after each logical unit of work
- **Always commit changes before switching tasks** - ensures work is saved and trackable
- Use descriptive commit messages that explain the "why" not just the "what"
- Follow conventional commit format when possible: `type: description`
- Common commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Include the Claude Code attribution footer for AI-assisted commits

## Common Tasks & Workflows

### Starting New Feature
1. Create feature branch
2. Add dependencies: `uv add package-name`
3. Write code with tests
4. Run quality checks: `uv run ruff format && uv run ruff check && uv run mypy src/`
5. Run tests: `uv run pytest`
6. Commit changes

### Preparing Release
1. Update version: `uv version patch` (or minor/major)
2. Update CHANGELOG.md if it exists
3. Commit changes
4. Create GitHub release (triggers auto-publish)

### Debugging Build Issues
- Check `pyproject.toml` syntax
- Verify all files are included in git
- Run `uv build` locally first
- Check GitHub Actions logs for specific errors

## File Generation Preferences
- Always generate complete, working files
- Include proper imports and dependencies
- Add error handling where appropriate
- Follow the established project structure
- Include basic tests for new functionality

## Quality Gates
Before any release:
- [ ] All tests pass (`uv run pytest`)
- [ ] Code is formatted (`uv run ruff format`)
- [ ] No linting errors (`uv run ruff check`)
- [ ] Type checking passes (`uv run mypy src/`)
- [ ] Version is bumped appropriately
- [ ] README is updated if needed

## Development Notes
- This project avoids traditional Python tools (pip, conda, virtualenv)
- UV handles everything: dependencies, environments, building, publishing
- Git operations happen through VS Code interface, not command line
- Releases are created via GitHub web interface
- CI/CD automates testing and publishing

## Helpful Context
- Developer is based in New Zealand (consider timezone for any scheduling)
- Prefers VS Code GUI over command line for Git operations
- Values automation and modern Python development practices
- Uses semantic versioning and conventional release workflows