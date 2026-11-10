import { useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";

function App() {
    const [website, setWebsite] = useState("");
    const [message, setMessage] = useState("");
    const [submitting, setSubmitting] = useState(false);

    async function submitWebsite(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setSubmitting(true);
        setMessage("");

        try {
            const response = await fetch("/api/website", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ website }),
            });
            if (response.status === 400) {
                setMessage("Enter a website URL.");
                return;
            }
            if (!response.ok) {
                throw new Error("Flask could not accept the URL.");
            }

            const result: { website: string } = await response.json();
            setMessage(`Submitted URL: ${result.website}`);
        } catch {
            setMessage("Could not submit the URL. Please try again.");
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <main>
            <h1>External Cybersecurity Analyzer</h1>
            <form onSubmit={submitWebsite}>
                <label htmlFor="website">Website URL</label>{" "}
                <input
                    id="website"
                    name="website"
                    type="url"
                    placeholder="https://example.com"
                    value={website}
                    onChange={(event) => setWebsite(event.target.value)}
                    required
                />{" "}
                <button disabled={submitting}>
                    {submitting ? "Submitting…" : "Submit"}
                </button>
            </form>
            <p role="status">{message}</p>
        </main>
    );
}

createRoot(document.getElementById("root")!).render(<App />);
