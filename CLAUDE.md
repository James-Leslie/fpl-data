# Summary
Python package for loading and transforming Fantasy Premier League API data.

# Tooling & Methodology
- **Package management**: uv only (never pip/conda)
- **Testing**: pytest with high coverage
- **Documentation**: MkDocs + GitHub Pages
- **Quality**: Pre-commit hooks with ruff, ty, pytest

# Code Standards
- Type hints and Google-style docstrings required
- Use f-strings, follow PEP 8
- Self-documenting code with clear naming
- Complete, working files with proper imports and tests

# Key Commands
```bash
uv add package-name              # Add dependencies
uv run pytest                    # Run tests
uv run mkdocs serve              # Preview docs
uv version --bump patch          # Version bump
uvx pre-commit run --all-files   # Manual quality check
```

  > Always use `uv` for dependency management (never edit pyproject.toml manually)

# Workflows

## Collaborative Development Workflow
1. **Plan & Track**: Use TodoWrite tool for multi-step tasks
2. **Iterative Development**: 
   - User requests changes/improvements
   - Claude analyzes and proposes solution
   - User reviews and provides feedback
   - Claude implements approved changes
3. **Quality & Commit**: Before moving on or finishing:
   - Run `uvx pre-commit run --all-files`
   - Fix any issues that arise
   - Create descriptive git commit

## CLAUDE.md Maintenance
**IMPORTANT**: This CLAUDE.md file should be kept up-to-date as the project evolves. When making significant changes to tooling, workflows, or project structure, update the relevant sections in this file. This ensures future AI assistance remains consistent with project conventions.
