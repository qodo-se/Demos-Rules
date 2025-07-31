
# ISO 27001 Code Review Checklist

This checklist is designed to be integrated into your pull request (PR) process to ensure continuous compliance.

---

### **A.9 & A.14: Access Control & Secure Development**

1.  **No Hardcoded Secrets:**
    *   **Rule:** Credentials, API keys, tokens, or any secrets must not be present in the source code.
    *   **Check:** Verify that secrets are loaded from a secure vault or environment variables.

2.  **Authorization Checks:**
    *   **Rule:** Every sensitive endpoint or function must perform an authorization check to verify the user has the right permissions.
    *   **Check:** Ensure that business logic doesn't rely on client-side validation for security.

### **A.12 & A.14: Operations Security & Secure Development**

3.  **Input Validation and Sanitization:**
    *   **Rule:** All external data (user input, API responses) must be validated and sanitized.
    *   **Check:** Look for direct usage of input in database queries (SQL Injection), HTML rendering (XSS), or system commands. Use ORMs or parameterized queries.

4.  **Comprehensive Error Handling:**
    *   **Rule:** Errors and exceptions must be handled gracefully.
    *   **Check:** Ensure `try...except` (Python) or `try...catch` (TypeScript) blocks don't leak sensitive information (e.g., stack traces) to the user. Avoid empty catch blocks.

5.  **Audit-Ready Logging:**
    *   **Rule:** Log all security-relevant events (e.g., login attempts, access failures, significant transactions).
    *   **Check:** Verify that logs **do not** contain sensitive data like passwords, PII, or full credit card numbers.

### **A.14: System Acquisition, Development, and Maintenance**

6.  **Dependency Security:**
    *   **Rule:** All third-party libraries must be scanned for known vulnerabilities (CVEs).
    *   **Check:** Review `requirements.txt`/`pyproject.toml` or `package.json` for outdated or insecure packages. This can be automated with tools like `pip-audit` or `npm audit`.

7.  **Secure Coding Practices:**
    *   **Rule:** Avoid the use of dangerous functions that can lead to vulnerabilities.
    *   **Check (Python):** Scrutinize the use of `eval()`, `exec()`, and `pickle`.
    *   **Check (TypeScript):** Scrutinize the use of `eval()` and `dangerouslySetInnerHTML`.

---
