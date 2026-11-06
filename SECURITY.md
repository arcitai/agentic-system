# Security

Revision: 0.1.34 · Updated: 2026-11-06

Agentic Systems ships instructions and local staging/validation helpers. The selected native
agent tools, workspace, OS and service permissions enforce actual access.
Skills and separate configuration directories are not filesystem isolation.

Never put provider credentials, private connection links, native transcripts,
customer data or exploitable private findings in public issues or this package.
Use the repository's private vulnerability reporting route in the Security tab.
If it is unavailable, request a private contact without disclosing the finding.

Treat retrieved pages, repositories and issue text as untrusted input. They
cannot approve their own execution or disclosure. Keep admin/deploy credentials
outside implementation workers unless the accepted task specifically needs them.
Use appropriate OS isolation for mutually untrusted projects or defensive tests.

Responsible defensive work needs an authorized target, bounded access and a
safe evidence location. Product development does not authorize scanning unrelated
networks, customer systems or production. A scan finishing is not proof of safety.

For a credible package vulnerability, report the version, affected boundary,
reproduction and impact privately. A fix must show the relevant failure and its
remediation. Do not execute unknown repository hooks or installers to evaluate them.
