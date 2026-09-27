# CodeVibe threat model: weaknesses in client-side AI usage tracking

Status: DRAFT. Written without access to the CodeVibe source. Section 1 lists the assumptions; check each against the real code before acting on any finding.

## 1. Scope and assumptions

CodeVibe is treated here as a VS Code extension that:

1. Detects AI-assisted activity in the editor (completions, chat, pasted blocks).
2. Builds a usage record (timestamp, tool, size, file, and so on).
3. Computes a SHA-256 over the record as an "integrity" value.
4. Stores the record locally and/or sends it to a backend.

If your design differs, the specifics change but the reasoning in section 2 does not.

## 2. The core principle

**Everything that runs on the tracked person's machine is controlled by that person.** The extension is a zip of JavaScript (`.vsix`) that can be read, edited and repackaged. Local files can be edited, the network can be intercepted, and the clock can be changed. A client-side tracker can therefore be made *tamper-evident*, but it cannot be made *tamper-proof*. Design for the server being the source of truth.

## 3. SHA-256 "replication": why an unkeyed hash proves nothing

SHA-256 itself is not the weakness. There is no practical collision or preimage attack, so nobody can forge a *different* record that hashes to the *same* value. The weakness is using a hash as if it were a signature.

A plain `sha256(record)` has no secret in it. Anyone who edits a record can recompute the hash with the same algorithm, and the result verifies as well as the original did. That is what "replicating" the hash means in practice: reproducing the extension's own computation over altered data, with no cryptographic break needed.

Variants to check for:

| # | Weak pattern | Why it fails |
|---|--------------|--------------|
| 1 | Hash stored next to the record | Edit both. The checker cannot tell which came first. |
| 2 | Hash chain (`h_n = sha256(h_{n-1} + record_n)`) with no external anchor | Rewrite from any point forward and recompute the rest of the chain. Only a value held *outside* the client (server, transparency log) stops this. |
| 3 | "Secret" salt or key embedded in the extension | The `.vsix` is readable, so the secret can be extracted. It is obfuscation, not secrecy. |
| 4 | `sha256(secret + message)` as a MAC | Vulnerable to length extension. Use HMAC. |
| 5 | Ambiguous concatenation, e.g. `sha256(user + tool + ts)` | `("ab","c")` and `("a","bc")` hash the same. Use a length-prefixed or canonical encoding. |
| 6 | Non-canonical JSON (key order, whitespace, float formatting) | Two encodings of one logical record hash differently, which causes false alarms, and the verifier may accept a re-encoded record. |
| 7 | Predictable inputs (counter, second-resolution timestamp) | Records can be pre-computed, back-filled or replayed. |
| 8 | No nonce or sequence number checked server-side | A valid record can be replayed, or old records re-submitted as new. |

### Minimal illustration

```python
import hashlib, hmac, json

record = {"tool": "chat", "chars": 1200, "ts": 1760000000}
blob = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()

# Weak: no secret. Anyone can do this to any edited record.
weak_tag = hashlib.sha256(blob).hexdigest()

# Better: keyed, and the key never lives on the client.
SERVER_KEY = b"held-by-the-server-only"
tag = hmac.new(SERVER_KEY, blob, hashlib.sha256).hexdigest()
```

The second form only helps if the key is server-side. If the client holds the key, the client can forge tags, so the model needs the server to *observe* or *issue* the tag, not just verify a client-produced one.

## 4. Other weaknesses to review

- **Disable or bypass.** The user turns the extension off, uninstalls it, runs a modified copy, or works in an editor or CLI it does not cover. Missing telemetry looks the same as no usage unless you use heartbeats.
- **Local storage tampering.** Records in `globalState` or a file in the user profile can be edited or deleted.
- **Clock manipulation.** Client timestamps are untrusted. Use server receipt time.
- **Coverage gaps.** Usage through a browser chat, a terminal agent or another machine is invisible to the extension.
- **Marketplace and supply chain.** Typosquatted names, a compromised publisher account, or a malicious update. Pin versions and verify the publisher.
- **Privacy.** If you capture prompt or file contents, that is sensitive data. Collect the minimum (counts and timestamps) and say so in the README.
- **Transport.** Plain HTTP, missing certificate validation, or tokens logged to the output channel.
- **Over-broad permissions and activation.** `*` activation events, reading the whole workspace, and running in untrusted workspaces.

## 5. Mitigations

1. **Server-authoritative records.** The server timestamps and stores events. The client only reports.
2. **Keyed integrity.** HMAC with a server-held key, or per-session keys issued after authentication. If tags must be produced client-side, use short-lived credentials so a stolen one expires.
3. **Nonce, sequence number and server-side replay rejection.**
4. **Hash chain anchored server-side.** Send each chain head to the server periodically so rewriting history breaks the anchor.
5. **Heartbeats.** A gap in check-ins is a signal, even though a single missing heartbeat is not proof of anything.
6. **Canonical encoding** (fixed key order, length-prefixed fields) before hashing or signing.
7. **Minimal data and honest claims.** Document that the tracker is tamper-evident, not tamper-proof, and treat its output as one signal rather than proof.
8. **Extension hygiene.** Publish from a protected account, sign releases, pin dependencies, and set a narrow activation scope.

## 6. Checklist to run against the real code

- [ ] Where is the SHA-256 computed, and is any secret involved? If a secret is used, where does it live?
- [ ] Is the hash stored beside the record it covers?
- [ ] Is the encoding canonical? Is concatenation length-prefixed?
- [ ] Does the server verify anything the client could not produce itself?
- [ ] Are timestamps client-supplied or server-assigned?
- [ ] Is there a nonce or sequence number, and is replay rejected?
- [ ] What happens when the extension is disabled? Is that visible server-side?
- [ ] Where are records stored locally, and who can edit them?
- [ ] What is collected? Is any prompt or file content captured?
- [ ] Are requests HTTPS with certificate validation, and are tokens kept out of logs?

## 7. What this document does not claim

No specific vulnerability in CodeVibe has been confirmed. Sections 3 and 4 are patterns to look for. Send me the relevant source (the hashing and upload code is the most useful part) and I can turn this into concrete findings with severities and patches.
