# Repository Guidelines

## Project Structure & Module Organization
- `backend/` contains the NestJS API, WebSocket gateway, Prisma client, and Redis integration. Core modules live in `src/chat`, `src/room`, `src/prisma`, and `src/redis`. Schema migrations and database definitions are under `backend/prisma/`.
- `frontend/` holds the React + Vite single-page app. UI components are in `src/components/`, TypeScript models in `src/types.ts`, and global styles in `src/index.css`.
- `docker-compose.yml` orchestrates PostgreSQL, Redis, backend, and frontend containers for local parity.
- Supporting docs (e.g., `readme.md`, compliance files) sit at the repository root for quick discovery.

## Build, Test, and Development Commands

```bash
# Backend (NestJS)
cd backend && npm install && npm run build      # compile to dist/
cd backend && npm run start:dev                # watch mode API/WebSocket server
cd backend && npm run lint                     # ESLint + Prettier integration

# Backend database tooling
cd backend && npx prisma migrate dev           # apply schema changes
cd backend && npx prisma generate              # refresh Prisma client

# Frontend (React + Vite)
cd frontend && npm install && npm run dev      # Vite dev server on :5173
cd frontend && npm run build                   # type-check + production bundle

# Full stack via containers
docker-compose up --build                      # start Postgres, Redis, API, UI
```

## Coding Style & Naming Conventions
- **Indentation**: 2 spaces across TypeScript/TSX; enforced by Prettier (`npm run format` in backend).
- **File naming**: PascalCase for React components (`ChatRoom.tsx`), kebab-case for configuration (`docker-compose.yml`), and lowerCamel for NestJS providers (`room.service.ts`).
- **Function/variable naming**: camelCase for functions (`handleJoinRoom`) and variables; NestJS providers/classes stay PascalCase (`RoomService`).
- **Linting**: ESLint + `@typescript-eslint` in both apps (`npm run lint`). Backend pairs ESLint with `eslint-config-prettier` to avoid formatting conflicts.

## Testing Guidelines
- **Framework**: No automated test harness is defined yet (no Jest/Cypress configs present). Reliability is currently ensured through manual end-to-end verification.
- **Test files**: Not applicable; mirror the existing module layout when introducing tests (e.g., `src/room/__tests__/room.service.spec.ts`).
- **Running tests**: Add a script (e.g., `npm run test`) when the first suite lands; until then, rely on `docker-compose up` and exercise flows through the UI.
- **Coverage**: No coverage targets documented; establish thresholds once the initial suite exists.

## Commit & Pull Request Guidelines
- **Commit format**: The history shows short, imperative subjects (e.g., `config`, `sync`, `.pr_agent.toml — security expert with STRIDE threat modeling`). Follow that minimal style unless a future CONTRIBUTING guide states otherwise.
- **PR process**: Not documented. Default to small, reviewable changes and describe any schema or API impacts in the pull request body.
- **Branch naming**: Unspecified. When collaborating, prefer descriptive prefixes such as `feature/room-permissions` or `fix/socket-reconnect` to ease tracking.

---

# Repository Tour

## 🎯 What This Repository Does

Real-Time Collaboration Tool provides a Socket.io-powered chat experience with persistent rooms so distributed teams can exchange messages instantly over the browser.

**Key responsibilities:**
- Serve a WebSocket API that brokers room membership, typing signals, and message fan-out (`backend/src/chat/chat.gateway.ts`).
- Persist rooms and messages in PostgreSQL via Prisma (`backend/prisma/schema.prisma`).
- Deliver a responsive React interface for room management and chat (`frontend/src/components`).

---

## 🏗️ Architecture Overview

### System Context
```
[React SPA (Vite, port 5173)] → [NestJS API + Socket.io Gateway (port 3000)] → [PostgreSQL 16]
                                                    ↓
                                              [Redis 7 pub/sub]
```

### Key Components
- **ChatGateway (backend/src/chat/chat.gateway.ts)** – WebSocket entry point handling `joinRoom`, `sendMessage`, `typing`, and Redis broadcasting to keep multi-instance deployments in sync.
- **RoomService & RoomController (backend/src/room)** – REST endpoints and Prisma-backed CRUD for rooms/messages, including history hydration on join.
- **PrismaService & schema.prisma** – Database access layer targeting PostgreSQL with two tables (`rooms`, `messages`).
- **RedisService (backend/src/redis/redis.service.ts)** – Provides publish/subscribe clients so chat events propagate beyond a single NestJS node.
- **React App + Components (frontend/src/App.tsx, components/)** – Handles username capture, room selection (`RoomList`), and live conversational UI (`ChatRoom`) via `socket.io-client`.

### Data Flow
1. User opens the Vite app, selects or creates a room via REST (`GET/POST /rooms`).
2. `ChatRoom` emits `joinRoom` over Socket.io; `ChatGateway` fetches the latest 50 messages through `RoomService` and returns `roomHistory`.
3. When a message is submitted, `ChatGateway` calls `RoomService.createMessage`, persists it via Prisma, emits `newMessage` to the room, and publishes to Redis (`room:<id>` channel).
4. Connected clients render updates, typing indicators, and membership notifications in real time; Redis fan-out ensures consistency if multiple backend instances run.

---

## 📁 Project Structure [Partial Directory Tree]

```
./
├── backend/
│   ├── src/
│   │   ├── app.module.ts            # Wires controllers, services, gateway
│   │   ├── chat/                    # Socket.io gateway logic
│   │   ├⁠── room/                    # REST controller + service
│   │   ├── prisma/                  # PrismaService wrapper
│   │   └── redis/                   # Redis connection helper
│   ├── prisma/schema.prisma         # PostgreSQL data model
│   └── package.json                 # Nest scripts & dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx                  # Top-level SPA logic
│   │   ├── components/              # RoomList + ChatRoom UI
│   │   ├── main.tsx                 # React entry point
│   │   └── types.ts                 # Shared TS interfaces
│   └── package.json                 # Vite scripts & deps
├── docker-compose.yml               # Local stack orchestration
├── readme.md                        # High-level usage guide
└── AGENTS.md                        # Contributor + technical guide
```

### Key Files to Know

| File | Purpose | When You'd Touch It |
|------|---------|---------------------|
| `backend/src/main.ts` | Bootstraps NestJS with CORS for the frontend origin. | Change ports or global middleware.
| `backend/src/app.module.ts` | Registers controllers, services, and gateways. | Add new modules or providers (e.g., Agent services).
| `backend/src/chat/chat.gateway.ts` | All Socket.io event handlers and Redis fan-out. | Extend real-time features or add new events.
| `backend/src/room/room.service.ts` | Prisma-based room/message CRUD. | Modify persistence rules, pagination, or validation.
| `backend/prisma/schema.prisma` | Database schema (rooms/messages). | Introduce new columns or relations; rerun migrations afterward.
| `frontend/src/App.tsx` | SPA orchestration: rooms fetch, username gate, layout. | Adjust layout or add new global flows.
| `frontend/src/components/RoomList.tsx` | Sidebar room management UI. | Enhance room metadata or filters.
| `frontend/src/components/ChatRoom.tsx` | Chat UI + socket wiring. | Add reactions, message states, or attachments.
| `docker-compose.yml` | Defines Postgres, Redis, backend, frontend services. | Update ports, env vars, or add supporting services.
| `readme.md` | Operational runbook for Docker-based workflows. | Keep quick-start instructions accurate after major changes.

---

## 🔧 Technology Stack

### Core Technologies
- **Language:** TypeScript (backend targets ES2021, frontend ES2020) for end-to-end type safety.
- **Framework:** NestJS 10 on the backend for structured modules/controllers; React 18 + Vite on the frontend for fast dev loops.
- **Database:** PostgreSQL 16 accessed via Prisma 5 for relational integrity and type-safe queries.
- **Realtime Layer:** Socket.io 4 (server + client) to manage WebSocket fallbacks with room semantics.
- **Cache/Broker:** Redis 7 using `ioredis` for pub/sub fan-out and future caching needs.
- **Containerization:** Docker & Compose to ship a reproducible stack (frontend, backend, Postgres, Redis).

### Key Libraries
- `@nestjs/websockets` & `@nestjs/platform-socket.io` – Socket gateway decorators and server wiring.
- `@prisma/client` / `prisma` – ORM + CLI tooling.
- `socket.io-client` – React-side real-time API.
- `tailwindcss` – Utility-first styling in the SPA.
- `@vitejs/plugin-react` – Fast HMR and JSX transform pipeline.

### Development Tools
- **ESLint + @typescript-eslint** – Lints both backend and frontend codebases.
- **Prettier** – Enforces consistent formatting (run via `npm run format` in backend or `eslint --fix`).
- **Prisma CLI** – Migration, schema validation, and client generation.
- **Docker Compose** – Standardizes multi-service development.

---

## 🌐 External Dependencies

### Required Services
- **PostgreSQL** – Stores `rooms` and `messages`. Schema defined in `prisma/schema.prisma`; connection string comes from `DATABASE_URL`.
- **Redis** – Provides pub/sub channels (`room:<id>`) and is mandatory for horizontal scalability.

### Optional Integrations
- None baked in yet. Additional services (e.g., vector stores or AI providers) can be mounted via new NestJS modules when the agent roadmap is implemented.

---

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/collaboration_db?schema=public
REDIS_HOST=redis
REDIS_PORT=6379
PORT=3000
FRONTEND_URL=http://localhost:5173

# Frontend (.env)
VITE_API_URL=http://localhost:3000
VITE_SOCKET_URL=http://localhost:3000
```

---

## 🔄 Common Workflows

### Spin up the full stack locally
1. Ensure Docker is running.
2. Execute `docker-compose up --build` from the repo root.
3. Wait for `Backend server is running` and `VITE ready` logs, then browse to `http://localhost:5173`.
**Code path:** `docker-compose.yml` → service Dockerfiles → `backend/src/main.ts` & `frontend/src/main.tsx`.

### Room creation and live chat flow
1. In the SPA, submit a username and create/select a room (`RoomList` triggers `POST /rooms`).
2. `ChatRoom` establishes a Socket.io connection and emits `joinRoom`.
3. `ChatGateway` returns history and broadcasts new messages + typing indicators.
4. Messages persist through `RoomService.createMessage` → Prisma → PostgreSQL.
**Code path:** `frontend/src/components/*` → `backend/src/chat/chat.gateway.ts` → `backend/src/room/room.service.ts` → `backend/prisma/schema.prisma`.

---

## 📈 Performance & Scale
- **Redis pub/sub**: Ensures that even with multiple backend replicas, messages stay consistent. Watch Redis connection health in `RedisService`.
- **Database indices**: `@@index([roomId])` on `Message` improves room-history fetches; consider pagination strategies when rooms exceed 50 messages.
- **Autoscaling**: Frontend is static; backend scaling hinges on Redis availability and Prisma connection pooling.

### Monitoring
- No built-in metrics yet. Start by adding NestJS interceptors or connect to an APM when productionizing.

---

## 🚨 Things to Be Careful About

### 🔒 Security Considerations
- **Authentication**: Currently absent by design. If you add auth, secure Socket.io namespaces and REST controllers simultaneously.
- **CORS & Origins**: `FRONTEND_URL` controls allowed origins; update `backend/src/main.ts` when deploying under another hostname.
- **Secrets**: Never commit `.env` files—sample values already exist in `*.env.example`.
- **Rate limiting**: Not implemented. Consider Nest rate-limit middleware before exposing the API publicly.

*Updated at: 2025-12-09 (UTC)*
*Last commit: cc85383ba6a84091caf61d00d87932e9b9862db6*
