const form = document.getElementById('f');
const button = document.getElementById('go');
const output = document.getElementById('out');
const error = document.getElementById('error');
const message = document.getElementById('message');
const cards = document.getElementById('cards');

function addCard(label, value, problem = false) {
  const card = document.createElement('div');
  card.className = problem ? 'card problem' : 'card';
  const heading = document.createElement('div');
  heading.className = 'k';
  heading.textContent = label;
  const content = document.createElement('div');
  content.className = 'v';
  content.textContent = String(value);
  card.append(heading, content);
  cards.append(card);
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  if (button.disabled) return;
  button.disabled = true;
  button.textContent = 'Checking…';
  form.setAttribute('aria-busy', 'true');
  output.hidden = true;
  error.hidden = true;
  message.textContent = 'Connecting to the website…';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: document.getElementById('url').value.trim() }),
      signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request failed. Try again.');
    document.getElementById('host').textContent = data.host;
    document.getElementById('status').className = 'status ' + (data.ok ? 'ok' : 'bad');
    document.getElementById('summary').textContent = data.ok
      ? 'TLS connection established; certificate accepted by the server’s trust store.'
      : 'TLS connection could not be verified or established.';
    cards.replaceChildren();
    if (data.ok) {
      addCard('Negotiated protocol', data.protocol);
      addCard('Negotiated cipher', data.cipher);
      addCard('Certificate expires', data.expires);
      addCard('Days remaining', data.days_left);
    } else {
      addCard('Connection problem', data.problem, true);
    }
    output.hidden = false;
    message.textContent = 'Check complete.';
  } catch (failure) {
    error.textContent = failure.name === 'AbortError'
      ? 'The request timed out. Try again.'
      : failure instanceof SyntaxError || failure instanceof TypeError
        ? 'Could not reach the backend. Check the connection and try again.'
        : failure.message;
    error.hidden = false;
    message.textContent = '';
  } finally {
    clearTimeout(timeout);
    button.disabled = false;
    button.textContent = 'Check TLS';
    form.setAttribute('aria-busy', 'false');
  }
});
