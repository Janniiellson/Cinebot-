import os
import sqlite3
import datetime
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Configuração da API TMDB ---

API_KEY_TMDB_V3 = "4abc90b934a3ac74d37919485ee6b0b4" # 
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YWJjOTBiOTM0YTNhYzc0ZDM3OTE5NDg1ZWU2YjBiNCIsIm5iZiI6MTc0NTI3MTc1My4zMDQsInN1YiI6IjY4MDZiYmM5YzNlOGU3NGI2ZGVlNmQ2MiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.-LYFb3r0oqmCKVCmi79_wtFp6yhOff6X7LEvTyA_xow" 
}

# --- Funções do Banco de Dados SQLite ---
def init_db():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            remetente TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_mensagem(session_id, remetente, conteudo):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO mensagens (session_id, remetente, conteudo) VALUES (?, ?, ?)',
                   (session_id, remetente, conteudo))
    conn.commit()
    conn.close()


def buscar_filme_por_nome(query):
    url = f"{BASE_URL}/search/movie"
    params = {"query": query, "language": "pt-BR"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data['results']:
            movie = data['results'][0]
            return (f"Encontrei o filme: {movie.get('title', 'N/A')}\n"
                    f"Lançamento: {movie.get('release_date', 'N/A')}\n"
                    f"Avaliação: {movie.get('vote_average', 'N/A')}/10\n"
                    f"Sinopse: {movie.get('overview', 'N/A')}")
        else:
            return "Desculpe, não encontrei nenhum filme com esse nome."
    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP do TMDB (filme por nome): {e.response.status_code} - {e.response.text}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora. (Erro HTTP)"
    except requests.exceptions.ConnectionError as e:
        print(f"Erro de Conexão do TMDB (filme por nome): {e}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora. (Erro de Conexão)"
    except requests.exceptions.Timeout as e:
        print(f"Erro de Timeout do TMDB (filme por nome): {e}")
        return "Desculpe, a conexão com o serviço de filmes excedeu o tempo limite."
    except requests.exceptions.RequestException as e:
        print(f"Erro geral de requisição do TMDB (filme por nome): {e}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora. (Erro de Requisição)"
    except Exception as e:
        print(f"Erro inesperado ao buscar filme por nome: {e}")
        return "Ocorreu um erro inesperado ao buscar o filme."

def buscar_top_filmes():
    url = f"{BASE_URL}/movie/now_playing"
    params = {"language": "pt-BR", "page": 1}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data['results']:
            top_movies = [f"{i+1}. {movie.get('title', 'N/A')} (Avaliação: {movie.get('vote_average', 'N/A')})"
                          for i, movie in enumerate(data['results'][:5])]
            return "Aqui estão alguns filmes em cartaz:\n" + "\n".join(top_movies)
        else:
            return "Não consegui encontrar filmes em cartaz no momento."
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao TMDB (top filmes): {e}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora."
    except Exception as e:
        print(f"Erro ao buscar top filmes: {e}")
        return "Ocorreu um erro ao buscar os top filmes."

def buscar_generos_tmdb():
    url = f"{BASE_URL}/genre/movie/list"
    params = {"language": "pt-BR"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data['genres']:
            return {genre['name'].lower(): genre['id'] for genre in data['genres']}
        else:
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao TMDB para gêneros: {e}")
        return {}
    except Exception as e:
        print(f"Erro ao buscar gêneros: {e}")
        return {}

GENRES_MAP = buscar_generos_tmdb()

def buscar_filmes_por_genero(genero_nome):
    if genero_nome.lower() not in GENRES_MAP:
        return f"Desculpe, não reconheço o gênero '{genero_nome}'. Tente um gênero comum como 'Ação', 'Comédia', 'Drama'."
    genre_id = GENRES_MAP[genero_nome.lower()]
    url = f"{BASE_URL}/discover/movie"
    params = {"language": "pt-BR", "sort_by": "popularity.desc", "with_genres": genre_id, "page": 1}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data['results']:
            genre_movies = [f"{i+1}. {movie.get('title', 'N/A')} (Avaliação: {movie.get('vote_average', 'N/A')})"
                            for i, movie in enumerate(data['results'][:5])]
            return f"Aqui estão alguns filmes do gênero '{genero_nome.capitalize()}':\n" + "\n".join(genre_movies)
        else:
            return f"Não encontrei filmes no gênero '{genero_nome}' no momento."
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao TMDB (filmes por gênero): {e}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora."
    except Exception as e:
        print(f"Erro ao buscar filmes por gênero: {e}")
        return "Ocorreu um erro ao buscar os filmes por gênero."

def buscar_filmes_por_ator(nome_ator):
    search_actor_url = f"{BASE_URL}/search/person"
    params_actor = {"query": nome_ator, "language": "pt-BR"}
    actor_id = None
    actor_name_found = nome_ator
    try:
        response_actor = requests.get(search_actor_url, headers=HEADERS, params=params_actor)
        response_actor.raise_for_status()
        actor_data = response_actor.json()
        if actor_data and actor_data['results']:
            actor_id = actor_data['results'][0]['id']
            actor_name_found = actor_data['results'][0]['name']
        else:
            return f"Desculpe, não encontrei o ator/atriz '{nome_ator}'."
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao TMDB (ator): {e}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora."
    except Exception as e:
        print(f"Erro ao buscar ator: {e}")
        return "Ocorreu um erro ao buscar o ator."

    if not actor_id:
        return f"Não encontrei o ator/atriz '{nome_ator}'."

    movies_by_actor_url = f"{BASE_URL}/person/{actor_id}/movie_credits"
    params_movies = {"language": "pt-BR"}
    try:
        response_movies = requests.get(movies_by_actor_url, headers=HEADERS, params=params_movies)
        response_movies.raise_for_status()
        movies_data = response_movies.json()
        if movies_data and movies_data['cast']:
            actor_movies = [f"{movie.get('title', 'N/A')} ({movie.get('release_date', 'N/A')[:4] if movie.get('release_date') else 'N/A'})"
                            for movie in sorted(movies_data['cast'], key=lambda x: x.get('popularity', 0), reverse=True)[:5]]
            return f"Aqui estão alguns filmes populares com {actor_name_found}:\n" + "\n".join(actor_movies)
        else:
            return f"Não encontrei filmes com {actor_name_found}."
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao TMDB (filmes do ator): {e}")
        return "Desculpe, não consegui me conectar ao serviço de filmes agora."
    except Exception as e:
        print(f"Erro ao buscar filmes do ator: {e}")
        return "Ocorreu um erro ao buscar os filmes do ator."

# --- Rotas da Aplicação Flask ---

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    return render_template('index.html')

@app.route('/pergunta', methods=['POST'])
def pergunta():
    user_message = request.json['mensagem'].lower().strip()
    session_id = session.get('session_id')

    print(f"DEBUG: Mensagem do usuário recebida: '{user_message}'")

    if not session_id:
        return jsonify({'resposta': 'Erro de sessão. Por favor, recarregue a página.'}), 400

    salvar_mensagem(session_id, 'user', user_message)

    bot_response = ""

    # --- Lógica de Decisão do Bot ---
    if "ajuda" in user_message:
        print("DEBUG: Entrou no comando 'ajuda'")
        bot_response = "Posso te ajudar com:\n- Buscar filme: 'nome do filme'\n- Top filmes: 'top filmes'\n- Filmes por gênero: 'gênero [nome do gênero]'\n- Filmes por ator: 'filmes com [nome do ator]'"
    elif "top filmes" in user_message:
        print("DEBUG: Entrou no comando 'top filmes'")
        bot_response = buscar_top_filmes()
    elif user_message.startswith("genero"):
        print("DEBUG: Entrou no comando 'genero'")
        genero_query = user_message.replace("genero", "").strip()
        if genero_query:
            bot_response = buscar_filmes_por_genero(genero_query)
        else:
            bot_response = "Qual gênero você gostaria de buscar? Ex: 'gênero comédia'"
    elif user_message.startswith("filmes com"):
        print("DEBUG: Entrou no comando 'filmes com'")
        actor_name = user_message.replace("filmes com", "").strip()
        if actor_name:
            bot_response = buscar_filmes_por_ator(actor_name)
        else:
            bot_response = "Por favor, digite o nome do ator/atriz. Ex: 'filmes com tom hanks'"
    elif user_message.startswith("buscar filme") or user_message.startswith("filme"):
        print("DEBUG: Entrou no comando 'buscar filme'")
        movie_name = user_message.replace("buscar filme", "").replace("filme", "").strip()
        if movie_name:
            bot_response = buscar_filme_por_nome(movie_name)
        else:
            bot_response = "Por favor, digite o nome do filme que deseja buscar."
    else:
        print("DEBUG: Nenhuma comando TMDB correspondente. Resposta padrão.")
        bot_response = "Desculpe, não entendi sua pergunta. Posso te ajudar com informações sobre filmes se você usar um dos comandos específicos."

    salvar_mensagem(session_id, 'bot', bot_response)
    return jsonify({'resposta': bot_response})

# --- Rotas para o Histórico de Conversas ---

@app.route('/historico')
def exibir_historico():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            session_id,
            MIN(timestamp) as start_time,
            (SELECT conteudo FROM mensagens WHERE session_id = m.session_id AND remetente = 'user' ORDER BY timestamp ASC LIMIT 1) as first_user_message
        FROM mensagens AS m
        GROUP BY session_id
        ORDER BY start_time DESC
    ''')
    conversations = cursor.fetchall()
    conn.close()

    conversations_data = []
    for conv in conversations:
        session_id, start_time, first_user_message = conv
        display_title = first_user_message if first_user_message else "Nova Conversa"
        if len(display_title) > 50:
            display_title = display_title[:47] + "..."
        conversations_data.append({
            'session_id': session_id,
            'start_time': datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M'),
            'title': display_title
        })
    return render_template('historico.html', conversations=conversations_data)

@app.route('/historico/<session_id>')
def get_conversation_messages(session_id):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT remetente, conteudo, timestamp FROM mensagens WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    messages = cursor.fetchall()
    conn.close()

    formatted_messages = []
    for msg in messages:
        remetente, conteudo, timestamp = msg
        formatted_messages.append({
            'remetente': remetente,
            'conteudo': conteudo,
            'timestamp': datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        })
    return jsonify(formatted_messages)

# --- Inicialização do Banco de Dados e Execução do Aplicativo ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)