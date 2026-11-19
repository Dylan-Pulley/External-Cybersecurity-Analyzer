import { useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";

function App() {
    const [message, setMessage] = useState("");
    const [sending, setSending] = useState(false);
    const [output, setOutput] = useState("Scan results will appear here.");

    async function sendUrl(event: FormEvent<HTMLFormElement>) {
        // Stop the page from reloading when we submit the form.
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const websiteUrl = form.get("website");
        const hasPermission = form.has("has_permission");
        setSending(true);
        setMessage("");
        setOutput(`Scanning ${websiteUrl}…\nWaiting for port and TLS results.`);

        try {
            // Send the URL to the Python server and wait for its reply.
            const response = await fetch("/api/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ website: websiteUrl, has_permission: hasPermission }),
            });
            if (!response.ok) {
                const reply = await response.json();
                throw new Error(
                    typeof reply.detail === "string"
                        ? reply.detail
                        : `Could not run the scan (HTTP ${response.status}).`
                );
            }

            if (!response.headers.get("content-type")?.includes("application/x-ndjson")) {
                throw new Error("The scan server returned an unexpected response format.");
            }

            if (!response.body) {
                throw new Error("The scan server returned no response body.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            const combined: {
                website: string;
                results: Record<string, unknown>;
            } = {
                website: String(websiteUrl),
                results: {},
            };

            function processLine(line: string) {
                if (!line.trim()) return;

                const reply = JSON.parse(line);
                Object.assign(combined.results, reply.results);

                setOutput(JSON.stringify(combined, null, 2));
                setMessage("Received scan results. Waiting for remaining checks.");
            }

            try {
                while (true) {
                    const { value, done } = await reader.read();

                    buffer += decoder.decode(value, { stream: !done });

                    let newline;
                    while ((newline = buffer.indexOf("\n")) !== -1) {
                        processLine(buffer.slice(0, newline));
                        buffer = buffer.slice(newline + 1);
                    }

                    if (done) break;
                }

                processLine(buffer);
            } finally {
                reader.releaseLock();
            }

            setMessage(
                "error" in combined.results
                    ? "The scan reported an error. See the results below."
                    : `Scan finished for ${combined.website}.`
            );
        } catch (error) {
            const detail = error instanceof Error ? error.message : "Could not run the scan. Please try again.";
            setMessage(detail);
            setOutput(`Error: ${detail}`);
        } finally {
            setSending(false);
        }
    }

    return (
        <main>
            <h1>External Cybersecurity Analyzer</h1>
            <form onSubmit={sendUrl}>
                <label htmlFor="website">Website URL</label>
                <input
                    id="website"
                    name="website"
                    type="url"
                    placeholder="https://example.com"
                    required
                />
                <label>
                    <input type="checkbox" name="has_permission" required />{" "}
                    I own this website or have permission to test it.
                </label>
                <button type="submit" disabled={sending}>
                    {sending ? "Scanning…" : "Run scan"}
                </button>
            </form>
            <p role="status">{message}</p>
            <div
                aria-label="Scan results"
                aria-busy={sending}
                tabIndex={0}
                style={{ background: "#111827", color: "#a7f3d0", padding: "1rem", borderRadius: "6px", minHeight: "180px", maxHeight: "500px", overflow: "auto" }}
            >
                <pre style={{ margin: 0, whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{output}</pre>
            </div>
        </main>
    );
}

createRoot(document.getElementById("root")!).render(<App />);
