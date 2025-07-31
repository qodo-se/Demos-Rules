# OWASP Top 10 Compliance Guidelines

## 1. Injection

- Always use parameterized queries or prepared statements for database access.
- Never concatenate user input into SQL, NoSQL, or command-line queries.
- Validate and sanitize all user inputs, including headers, cookies, and URL parameters.

## 2. Broken Authentication

- Use strong, adaptive password policies (minimum length, complexity, no reuse).
- Implement multi-factor authentication (MFA) wherever possible.
- Never store passwords in plaintext; always use strong, salted hashing algorithms (e.g., bcrypt, Argon2).
- Invalidate sessions on logout and after password changes.

## 3. Sensitive Data Exposure

- Always use HTTPS/TLS for all data in transit.
- Encrypt sensitive data at rest using strong algorithms (e.g., AES-256).
- Never log sensitive information (passwords, credit card numbers, etc.).
- Use secure headers (e.g., Strict-Transport-Security).

## 4. XML External Entities (XXE)

- Disable XML external entity processing in all XML parsers.
- Prefer JSON over XML for data exchange.
- Validate and sanitize all XML input.

## 5. Broken Access Control

- Enforce access control on the server side for every request.
- Deny access by default; explicitly grant permissions.
- Never rely on client-side checks for authorization.
- Regularly review and test access control rules.

## 6. Security Misconfiguration

- Disable directory listing and remove default credentials.
- Keep all software and dependencies up to date.
- Use security headers (Content-Security-Policy, X-Frame-Options, etc.).
- Automate security configuration checks in CI/CD pipelines.

## 7. Cross-Site Scripting (XSS)

- Escape all untrusted data before rendering in the browser.
- Use frameworks that automatically escape XSS by design.
- Implement Content Security Policy (CSP).
- Validate and sanitize user input on both client and server sides.

## 8. Insecure Deserialization

- Avoid deserializing objects from untrusted sources.
- Use safe data formats (e.g., JSON instead of binary formats).
- Implement integrity checks (e.g., digital signatures) on serialized data.
- Restrict and monitor deserialization endpoints.

## 9. Using Components with Known Vulnerabilities

- Regularly scan dependencies for vulnerabilities (e.g., using Snyk, Dependabot).
- Only use actively maintained libraries and frameworks.
- Remove unused dependencies.
- Subscribe to security advisories for your tech stack.

## 10. Insufficient Logging & Monitoring

- Log all authentication events, access control failures, and input validation errors.
- Ensure logs are protected from tampering and stored securely.
- Monitor logs and set up alerts for suspicious activities.
- Regularly review and test incident response procedures.

---

**For Code Reviewers:**

- Verify adherence to these guidelines in every code review.
- Use automated tools to check for common OWASP Top 10 issues.
- Require evidence of security testing (static/dynamic analysis, penetration testing).
- Reject code that does not meet these standards.
