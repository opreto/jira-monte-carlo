## Architectural Documentation

- Any architectural change to the system should be documented in a LADR document in the `docs/architecture` directory of the project. The LADR status should be "ACCEPTED", and it should be simple to understand, and designed for the entire `docs/architecture` directory to provide a historical record of major architectural decisions and their rationale.

## Development Workflow

- Your workflow should be: plan -> design failing tests -> implement -> flesh out tests -> update documentation as appropriate -> commit/push.

## CLI Guidelines

- When generating reports from the CLI, ensure they always get saved in the `reports` directory.
- Any report you generate should go in the reports/ directory. Documentation should go in the docs/ directory. Keep the top level directory of the project well organized and clean.