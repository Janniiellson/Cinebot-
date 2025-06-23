document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.getElementById('menuButton');
    const sidebar = document.getElementById('sidebar');
    const newChatButton = document.getElementById('newChatButton');
    const conversationItems = document.querySelectorAll('.conversation-item a');
    const conversationDisplay = document.getElementById('conversationDisplay');
    const currentConversationTitle = document.getElementById('currentConversationTitle');

    // Lógica para o botão de menu da sidebar
    menuButton.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        document.body.classList.toggle('sidebar-active');
    });

    // Lógica para o botão "Nova Conversa" (apenas redireciona)
    newChatButton.addEventListener('click', (e) => {
        e.preventDefault(); // Previne o comportamento padrão do link
        // Redireciona para a página principal, que gerará uma nova sessão de chat
        window.location.href = '/';
    });

    // Função para carregar e exibir mensagens de uma conversa
    async function loadConversation(sessionId, title) {
        // Remove a classe 'selected' de todos os itens e adiciona ao clicado
        conversationItems.forEach(item => item.classList.remove('selected'));
        document.querySelector(`[data-session-id="${sessionId}"]`).classList.add('selected');

        currentConversationTitle.textContent = `Conversa: ${title.split('(')[0].trim()}`; // Remove a data do título principal

        conversationDisplay.innerHTML = ''; // Limpa o display da conversa

        try {
            const response = await fetch(`/historico/${sessionId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const messages = await response.json();

            messages.forEach(msg => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', msg.remetente);
                messageElement.innerHTML = `${msg.remetente === 'user' ? 'Você' : 'CineBot'}: ${msg.conteudo} <span class="timestamp">${msg.timestamp}</span>`;
                conversationDisplay.appendChild(messageElement);
            });
            conversationDisplay.scrollTop = conversationDisplay.scrollHeight; // Auto-scroll
        } catch (error) {
            console.error('Erro ao carregar conversa:', error);
            conversationDisplay.innerHTML = '<div class="message bot">Erro ao carregar esta conversa.</div>';
        }
    }

    // Adicionar event listener para cada item de conversa na sidebar
    conversationItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const sessionId = item.dataset.sessionId;
            const title = item.textContent;
            loadConversation(sessionId, title);
            sidebar.classList.remove('active'); // Esconde a sidebar após selecionar conversa
            document.body.classList.remove('sidebar-active');
        });
    });

    // Carregar a última conversa automaticamente ao carregar a página, se houver
    if (conversationItems.length > 0) {
        const lastConversation = conversationItems[0];
        const lastSessionId = lastConversation.dataset.sessionId;
        const lastTitle = lastConversation.textContent;
        loadConversation(lastSessionId, lastTitle);
    }
});