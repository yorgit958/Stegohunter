# Contributing to StegoHunter

Thank you for your interest in contributing to StegoHunter! This guide will help you get started.

## Development Setup

### Prerequisites

- Docker Desktop v24+
- Node.js v20+
- Python 3.10+
- Git

### Local Development

```bash
# Clone the repo
git clone https://github.com/nik1740/Stegohunter.git
cd Stegohunter

# Set up environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Start backend services
docker compose up -d redis minio
docker compose up -d --build gateway-service image-analysis-service neutralization-service notification-service

# Start frontend
cd frontend
npm install
npm run dev
```

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below.

3. **Test locally** — ensure the frontend builds and Docker containers start:
   ```bash
   cd frontend && npm run build  # Verify no type errors
   docker compose build          # Verify Docker builds
   ```

4. **Commit** with a descriptive message:
   ```bash
   git commit -m "feat: description of change"
   ```

5. **Push** and open a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `refactor:` | Code refactoring |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks |

## Coding Standards

### Python (Backend Services)
- Use **type hints** for all function signatures
- Follow **PEP 8** style guidelines
- Use `async/await` for all I/O operations
- Include docstrings for public functions

### TypeScript (Frontend)
- Use **strict TypeScript** — no `any` types where avoidable
- Use **functional components** with hooks
- Keep components focused and under 200 lines
- Use the existing shadcn/ui component library

### Docker
- Keep Dockerfiles minimal and use multi-stage builds where possible
- Never include secrets in Docker images
- Use `.dockerignore` to exclude unnecessary files

## Architecture Decisions

- **Gateway Pattern**: All frontend requests go through the Gateway service, which handles auth and routing
- **Event-Driven**: Real-time updates use Redis Pub/Sub → WebSocket, not polling
- **Ensemble Detection**: Multiple independent engines vote on whether an image contains steganography
- **MinIO for Storage**: All uploaded images are stored in MinIO, never on the filesystem

## Need Help?

- Open a [GitHub Issue](https://github.com/nik1740/Stegohunter/issues) for bugs or feature requests
- Check the [README](./README.md) for setup and deployment guides
