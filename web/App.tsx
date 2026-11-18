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
            if (!response.headers.get("content-type")?.includes("application/json")) {
                throw new Error(`The scan server returned a webpage instead of results (HTTP ${response.status}). Refresh and try again. If it keeps happening, report this status code.`);
            }
            const reply = await response.json();
            if (!response.ok) {
                const detail = typeof reply.detail === "string" ? reply.detail : "Could not run the scan.";
                throw new Error(`${detail} (HTTP ${response.status})`);
            }

            setMessage(`Scan finished for ${reply.website}. Check each tool's results below.`);
            setOutput(JSON.stringify(reply, null, 2));
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
