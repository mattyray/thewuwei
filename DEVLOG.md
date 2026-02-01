# WuWei Development Log

A running record of TDD-driven development decisions. Each entry captures: what test was written, what design decision it forced, and what emerged from the process.

Built with Claude Code (Opus 4.5) as a pair programming partner.

---

## 2026-02-01 — Project Setup

### What happened
- Created CLAUDE.md (project context) and SPEC.md (full technical specification)
- Initialized git repo, connected to GitHub (github.com/mattyray/thewuwei)
- Set up .gitignore for Django/Next.js/Docker stack

### Design decisions
- **Multi-tenancy approach:** Simple user-scoped queries (every model gets a `user` ForeignKey, every query filters by `request.user`). No tenant abstraction needed — this is a personal practice app, not a team tool.
- **TDD strategy:** Tests drive design at every layer — model tests force schema decisions, API tests force auth/scoping, agent tool tests force interface design. Multi-tenancy is tested at every layer, not bolted on.

### Key insight
> The multi-tenancy guarantee isn't an afterthought — it's baked in because we test for it at every layer. The test that user_a can't see user_b's journal entry drives the `get_queryset` implementation in every viewset.

---

## 2026-02-01 — Docker + Django Skeleton + User Model (TDD) `#tdd` `#architecture` `#ai-pairing`

### What happened
- Built Docker Compose setup: pgvector/pg16, redis, backend, celery, celery-beat
- Created Django project skeleton: config/ (settings, urls, asgi, wsgi, celery), apps/users/
- Wrote 14 tests for the User model BEFORE writing the model (true TDD)
- All 14 tests passing

### Tests written (and what they drove)

| Test | Design decision it forced |
|------|---------------------------|
| `test_user_model_is_custom` | AUTH_USER_MODEL must point to our custom model |
| `test_create_user_with_email` | Email-based auth, no username field |
| `test_create_user_requires_email` | UserManager must validate email presence |
| `test_email_is_unique` | `unique=True` on email field |
| `test_email_is_normalized` | Manager must call `normalize_email()` |
| `test_no_username_field` | `username = None` to remove inherited field |
| `test_str_returns_email` | `__str__` returns email |
| `test_default_timezone` | Default timezone = America/New_York |
| `test_default_reminder_time` | Default reminder = 20:00 (using `time` object, not string) |
| `test_default_reminder_enabled` | Reminders on by default |
| `test_default_reflections_today` | Rate limiting counter starts at 0 |
| `test_default_api_key_empty` | BYO API key starts empty |
| `test_create_superuser` | Superuser gets is_staff + is_superuser |
| `test_two_users_exist_independently` | Multi-tenancy foundation — two users coexist |

### TDD moment
The `test_default_reminder_time` test initially failed because the model used `default="20:00"` (a string), but the test expected a proper `time` object. The test caught a subtle bug: Django's `TimeField` stores string defaults as strings rather than converting them. **The test drove us to use `default=time(20, 0)`** — a proper Python time object. This is exactly how TDD is supposed to work: the test defines the contract, the implementation conforms.

### Dependency resolution
- `django-celery-beat` doesn't support Django 6 yet → chose **Django 5.2 LTS** (security updates through 2028)
- `pytest-asyncio` requires `pytest<9` → pinned **pytest 8.3.4**
- `django-pgvector` doesn't exist on PyPI → using `pgvector` package which includes Django support via `pgvector.django`

---

<!-- New entries will be added above this line -->
