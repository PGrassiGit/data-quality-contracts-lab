# Architecture

## Planned Data Flow

Dataset -> contract loader -> validators -> report writer -> quarantine

## Tradeoffs

- Start with local files instead of a service.
- Keep contracts in version control.
- Add a UI only after the checks are useful from the CLI.
