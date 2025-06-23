document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const menuButton = document.getElementById('menuButton');
    const sidebar = document.getElementById('sidebar');
    const newChatButton = document.getElementById('newChatButton');
    const showCommandsButton = document.getElementById('showCommandsButton');

    // Função auxiliar para adicionar mensagens ao chat
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        // Usar innerHTML permite que a mensagem contenha HTML (como a seção de comandos)
        messageElement.innerHTML = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll para o final
    }

    // Função para enviar mensagem ao backend Flask
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        appendMessage('user', `Você: ${message}`);
        userInput.value = ''; // Limpa o input após enviar

        try {
            const response = await fetch('/pergunta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mensagem: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            appendMessage('bot', `CineBot: ${data.resposta}`);
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            appendMessage('bot', 'CineBot: Desculpe, tive um problema ao me comunicar. Tente novamente mais tarde.');
        }
    }

    // Event listeners para o botão de envio e Enter no input
    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Lógica para o botão de menu da sidebar (hambúrguer)
    menuButton.addEventListener('click', () => {
        sidebar.classList.toggle('active'); // Adiciona/remove a classe 'active' na sidebar para mostrá-la/escondê-la
        document.body.classList.toggle('sidebar-active'); // Adiciona/remove a classe 'sidebar-active' no body para ajustar o layout do chat
    });

    // Lógica para o botão "Nova Conversa" na sidebar
    newChatButton.addEventListener('click', (e) => {
        e.preventDefault(); // Previne o comportamento padrão do link
        // Limpa o chat e recria a mensagem inicial do bot, incluindo a seção de comandos
        chatMessages.innerHTML = `
            <div class="message bot">
                Olá, cinéfilo! Eu sou o CineBot. 😊
                <p>Se estiver com dúvidas, digite "ajuda".</p>
                <div id="commands-section">
                    <h3>🎬 Comandos do CineBot:</h3>
                    <div class="command-item" onclick="toggleCommand('comando-1')">
                        <span class="command-title">1. Buscar filme</span>
                        <div id="comando-1" class="command-details hidden">
                            <p>Pergunte pelo nome do filme!</p>
                            <p class="example">Exemplo: <code>interestelar</code>, <code>matrix</code></p>
                        </div>
                    </div>
                    <div class="command-item" onclick="toggleCommand('comando-2')">
                        <span class="command-title">2. Top filmes</span>
                        <div id="comando-2" class="command-details hidden">
                            <p>Veja os filmes em cartaz no cinema agora.</p>
                            <p class="example">Exemplo: <code>top filmes</code></p>
                        </div>
                    </div>
                    <div class="command-item" onclick="toggleCommand('comando-3')">
                        <span class="command-title">3. Filmes por gênero</span>
                        <div id="comando-3" class="command-details hidden">
                            <p>Pergunte sobre filmes de um gênero específico.</p>
                            <p class="example">Exemplo: <code>gênero comédia</code>, <code>gênero ação</code></p>
                        </div>
                    </div>
                    <div class="command-item" onclick="toggleCommand('comando-4')">
                        <span class="command-title">4. Filmes por ator/atriz</span>
                        <div id="comando-4" class="command-details hidden">
                            <p>Veja filmes com um ator ou atriz específico.</p>
                            <p class="example">Exemplo: <code>filmes com tom hanks</code>, <code>filmes com natalie portman</code></p>
                        </div>
                    </div>
                    <div class="command-item" onclick="toggleCommand('comando-5')">
                        <span class="command-title">5. Sair</span>
                        <div id="comando-5" class="command-details hidden">
                            <p>Encerre a conversa com o CineBot.</p>
                            <p class="example">Exemplo: <code>sair</code></p>
                        </div>
                    </div>
                </div>
                <p class="disclaimer-bot">
                    **Dica:** Seja criativo com suas perguntas! O CineBot adora conversar sobre cinema! 🍿🎬
                </p>
            </div>
        `;
        sidebar.classList.remove('active'); // Esconde a sidebar após iniciar nova conversa
        document.body.classList.remove('sidebar-active');
        userInput.focus(); // Coloca o foco de volta no input de texto
    });

    // Função global para expandir/colapsar os detalhes do comando
    // Precisa ser global (window.toggleCommand) pois é chamada via onclick no HTML
    window.toggleCommand = function(commandId) {
        const details = document.getElementById(commandId);
        if (details) {
            details.classList.toggle('hidden'); // Adiciona/remove a classe 'hidden' para mostrar/esconder
            // Rola o chat para garantir que o comando expandido/colapsado esteja visível
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    // Lógica para o botão "Comandos" na sidebar
    showCommandsButton.addEventListener('click', (e) => {
        e.preventDefault(); // Previne o comportamento padrão do link
        const commandsSection = document.getElementById('commands-section');
        if (commandsSection) {
            // Rola o chat para a seção de comandos de forma suave
            commandsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        sidebar.classList.remove('active'); // Esconde a sidebar após clicar no botão
        document.body.classList.remove('sidebar-active');
    });

});