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
  const history = [];

  function appendMessage(text, isUser) {
    const div = document.createElement('div');
    div.className = `chat-msg chat-msg--${isUser ? 'user' : 'bot'}`;
    div.textContent = text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  function localReply(message) {
    const turns = history.filter((item) => item.role === 'user').length;
    if (turns <= 1) {
      return {
        reply: 'Gracias. ¿Tu empresa vende, atiende clientes o pierde tiempo en tareas a mano?',
        ready_for_lead: false,
      };
    }
    if (turns === 2) {
      return {
        reply: '¿Qué usáis hoy (WhatsApp, CRM, correo o Excel) y qué se atasca?',
        ready_for_lead: false,
      };
    }
    return {
      reply: 'Encaja un diagnóstico y, si hay caso, un piloto en 7 días. ¿Preparo el resumen por correo?',
      ready_for_lead: true,
    };
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
        body: JSON.stringify({ message, history: history.slice(0, -1) }),
      });
      data = await response.json();
    } catch (error) {
      data = localReply(message);
    }
    thinking.remove();

    const reply = data.reply || '¿Puedes contarme un poco más del negocio?';
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
    const subject = encodeURIComponent('Diagnóstico AplicamosIA');
    const body = encodeURIComponent(
      `Correo: ${email}\nEmpresa: ${company || '—'}\n\nConversación:\n${transcript}`
    );
    window.location.href = `mailto:merlin655040999@gmail.com?subject=${subject}&body=${body}`;
  });
}
