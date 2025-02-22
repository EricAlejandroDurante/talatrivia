# TalaTrivia

## 🚀 Descripción

TalaTrivia es un juego de preguntas y respuestas donde los usuarios participan en trivias sobre temas de recursos humanos. La API permite la gestión de usuarios, preguntas, trivias, la participación de los usuarios y la visualización de un ranking basado en puntajes.

## 📑 Funcionalidades

- **Usuarios:** Crear y listar usuarios (ID, nombre y correo electrónico).
- **Preguntas:** Crear y listar preguntas con opciones múltiples, categorizadas por dificultad (fácil, medio, difícil).
- **Trivias:** Crear trivias con nombre, descripción, selección de preguntas y asignación de usuarios.
- **Participación:** Permitir a los usuarios responder preguntas y calcular su puntaje.
- **Ranking:** Visualizar un ranking de usuarios basado en sus puntajes.

## 🛠 Tecnologías

- **Backend:** Django + Django REST Framework
- **Autenticación:** (Opcional) Django Auth o JWT
- **Base de Datos:** PostgreSQL
- **Contenerización:** Docker & Docker Compose
- **Gestión de Dependencias:** Poetry

## 🚦 Requisitos previos

- Python 3.12+
- Docker y Docker Compose
- Poetry
- Django 5.12

## 🤔 Supuestos

- Autenticación de Usuarios: Se asume que la autenticación se maneja mediante oauth2.0 de manera que se pueda autenticar por parte del servidor propio o aplicaciones externas.

- Respuestas a las Preguntas: Las preguntas pueden tener una variada cantidad de alternativas, con una respuesta correcta o muchas respuestas correctas.

- Las preguntas para cada trivia pueden ser variadas, es decir, una trivia puede tener más o menos preguntas que otras.

- Asignación de Trivias a Usuarios: Se asume que un usuario puede participar en múltiples trivias, pero no repetir la misma trivia.

- Sistema de Puntuación: Si un usuario responde incorrectamente, no se restan puntos (puntaje mínimo es 0).

- Control de Acceso: Se implementan roles de usuario (admin, jugador). Los admins pueden gestionar trivias y preguntas, mientras que los jugadores solo pueden participar en las trivias.

- Estado de las Trivias: Las trivias pueden tener un estado de activa o finalizada para controlar si aún se pueden responder.

- Se asumirá que el docker-compose estará en la parte del servidor, pero por razones de ser repositorio de prueba estará dentro de este.

## ⚙️ Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/EricAlejandroDurante/talatrivia.git
cd talatrivia
```

2. Instala las dependencias con poetry:

```bash
poetry install
```

3. Para los servidores de desarrollo ejecuta:

```bash
poetry run python manage_development.py runserver
poetry run celery -A config worker --loglevel=info
```

4. Para los servidores de producción:

```bash
docker-compose up -d --build
```
