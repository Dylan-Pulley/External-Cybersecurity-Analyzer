import { useState, type FormEvent } from "react";
import { createRoot } from "react-dom/client";

function App() {
    const [websiteUrl, setWebsiteUrl] = useState("");
    const [formMessage, setFormMessage] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function submitWebsite(event: FormEvent<HTMLFormElement>) {
        // Keep the page open while we send the URL to Flask.
        event.preventDefault();
        setIsSubmitting(true);
        setFormMessage("");

        try {
            const response = await fetch("/api/website", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ website: websiteUrl }),
            });
            if (response.status === 400) {
                setFormMessage("Enter a website URL.");
                return;
            }
            if (!response.ok) {
                throw new Error("Flask could not accept the URL.");
            }

            const reply: { website: string } = await response.json();
            setFormMessage(`Submitted URL: ${reply.website}`);
        } catch {
            setFormMessage("Could not submit the URL. Please try again.");
        } finally {
            setIsSubmitting(false);
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
                    value={websiteUrl}
                    onChange={(event) => setWebsiteUrl(event.target.value)}
                    required
                />{" "}
                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Submitting…" : "Submit"}
                </button>
            </form>
            <p role="status">{formMessage}</p>
        </main>
    );
}

// Put the React page inside the root element in index.html.
createRoot(document.getElementById("root")!).render(<App />);
