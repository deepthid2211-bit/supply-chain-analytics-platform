# Security Policy

## Credential Safety

**Do not commit credentials, API keys, or secrets to this repository.**

This project connects to Snowflake, OpenAI, Groq, and other services that require authentication. All sensitive configuration must be kept out of version control.

## Configuration Templates

A configuration template is provided at:

```
config/config.template.yaml
```

To set up your local configuration:

1. Copy the template to create your personal config file:
   ```bash
   cp config/config.template.yaml config/config.yaml
   ```
2. Fill in your actual credentials in `config/config.yaml`.
3. **Never commit `config/config.yaml`** -- it is included in `.gitignore` for your protection.

## Environment Variables

For services that use environment variables (e.g., OpenAI API keys, Groq API keys):

1. Copy the environment template if one is provided:
   ```bash
   cp .env.template .env
   ```
2. Populate `.env` with your actual keys.
3. **Never commit `.env`** -- it is included in `.gitignore`.

## What Is Safe to Commit

- `config/config.template.yaml` -- contains placeholder values only
- `.env.template` -- contains placeholder values only
- All source code, SQL models, and documentation

## What Must Never Be Committed

- `config/config.yaml` -- contains real credentials
- `.env` -- contains real API keys
- Any file containing passwords, tokens, or connection strings
- Snowflake account identifiers paired with credentials
- API keys for OpenAI, Groq, or any other service

## Reporting a Vulnerability

If you discover that credentials have been accidentally committed or find any other security issue, please:

1. **Do not open a public issue.**
2. Contact the repository owner directly at desharajudeepthi@gmail.com.
3. Rotate any exposed credentials immediately.

## Best Practices

- Use environment variables or config files excluded from version control for all secrets.
- Review `git diff` before every commit to ensure no credentials are staged.
- Use `git-secrets` or similar tools to scan for accidental credential commits.
- Rotate credentials regularly and immediately if exposure is suspected.
