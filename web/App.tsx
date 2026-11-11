import { useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";

function App() {
    const [message, setMessage] = useState("");
    const [sending, setSending] = useState(false);

    async function sendUrl(event: FormEvent<HTMLFormElement>) {
        // Stop the page from reloading when we submit the form.
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const websiteUrl = form.get("website");
        setSending(true);
        setMessage("");

        try {
            // Send the URL to the Python server and wait for its reply.
            const response = await fetch("/api/website", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ website: websiteUrl }),
            });
            if (!response.ok) {
                throw new Error("Could not submit the URL.");
            }

            const reply: { website: string } = await response.json();
            setMessage(`Submitted URL: ${reply.website}`);
        } catch {
            setMessage("Could not submit the URL. Please try again.");
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
                <button type="submit" disabled={sending}>
                    {sending ? "Sending…" : "Submit"}
                </button>
            </form>
            <p role="status">{message}</p>
        </main>
    );
}

createRoot(document.getElementById("root")!).render(<App />);
