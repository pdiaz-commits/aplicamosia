const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.main-nav');

if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    navigation.classList.toggle('is-open', !isOpen);
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.matches('a')) {
      menuButton.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
    }
  });
}

const chatRoot = document.getElementById('agencyChat');
if (chatRoot) {
  const log = document.getElementById('chatLog');
  const form = document.getElementById('chatForm');
  const input = document.getElementById('chatInput');
  const leadPanel = document.getElementById('leadPanel');
  const leadForm = document.getElementById('leadForm');
  const apiUrl = chatRoot.dataset.apiUrl || '/api/chat/';
  const lang = chatRoot.dataset.lang || 'es';
  const i18nNode = document.getElementById('chat-i18n');
  const i18n = i18nNode ? JSON.parse(i18nNode.textContent) : {};
  const history = [];

  function appendMessage(text, isUser) {
    const div = document.createElement('div');
    div.className = `chat-msg chat-msg--${isUser ? 'user' : 'bot'}`;
    div.textContent = text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  function localReply() {
    const turns = history.filter((item) => item.role === 'user').length;
    const lines = i18n.fallback || [];
    if (turns <= 1) {
      return { reply: lines[0] || '', ready_for_lead: false };
    }
    if (turns === 2) {
      return { reply: lines[1] || '', ready_for_lead: false };
    }
    return { reply: lines[2] || '', ready_for_lead: true };
  }

  document.querySelectorAll('[data-chat-example]').forEach((button) => {
    button.addEventListener('click', () => {
      input.value = button.getAttribute('data-chat-example') || '';
      input.focus();
    });
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, true);
    history.push({ role: 'user', content: message });
    input.value = '';
    input.disabled = true;

    const thinking = document.createElement('div');
    thinking.className = 'chat-msg chat-msg--bot';
    thinking.textContent = '…';
    log.appendChild(thinking);

    let data;
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history: history.slice(0, -1), lang }),
      });
      data = await response.json();
    } catch (error) {
      data = localReply();
    }
    thinking.remove();

    const reply = data.reply || i18n.more || '';
    appendMessage(reply, false);
    history.push({ role: 'assistant', content: reply });
    if (data.ready_for_lead && leadPanel) leadPanel.hidden = false;
    input.disabled = false;
    input.focus();
  });

  leadForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    const email = document.getElementById('leadEmail').value.trim();
    const company = document.getElementById('leadCompany').value.trim();
    const transcript = history.map((item) => `${item.role}: ${item.content}`).join('\n');
    const subject = encodeURIComponent(i18n.subject || 'AplicamosIA');
    const body = encodeURIComponent(
      `${i18n.email || 'Email'}: ${email}\n${i18n.company || 'Company'}: ${company || '—'}\n\n${i18n.chat || 'Conversation'}:\n${transcript}`
    );
    window.location.href = `mailto:merlin655040999@gmail.com?subject=${subject}&body=${body}`;
  });
}
