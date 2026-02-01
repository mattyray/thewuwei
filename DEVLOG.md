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

## 2026-02-01 — Core Data Models (TDD) `#tdd` `#architecture`

### What happened
- Wrote 41 new tests across 4 test files BEFORE writing any model code
- Implemented 7 models across 4 apps: JournalEntry, DailyCheckin, GratitudeEntry, WeeklySummary, Todo, Mantra, ChatMessage
- All 55 tests passing (14 user + 41 new) — all green on first model implementation run

### Apps created

| App | Models | Tests |
|-----|--------|-------|
| `journal` | JournalEntry, DailyCheckin, GratitudeEntry, WeeklySummary | 17 |
| `todos` | Todo | 8 |
| `mantras` | Mantra | 7 |
| `chat` | ChatMessage | 5 |

### What the tests drove

**unique_together constraints:** Every model that represents a daily record (JournalEntry, DailyCheckin, GratitudeEntry) has `unique_together = ["user", "date"]`. The tests for "can't have two entries on the same day" directly forced this constraint. But the tests also verify "two different users CAN have entries on the same date" — proving the constraint scopes correctly.

**Multi-tenancy at model level:** Every app has explicit multi-tenancy tests (`test_users_have_separate_*`). These tests filter by user and assert the count is 1, proving that `user` ForeignKey + query filtering works. This pattern will compound when we add API viewsets — the API tests will verify the same isolation at the HTTP level.

**Ordering contracts:**
- JournalEntry: `-date` (newest first) — makes sense for reading history
- ChatMessage: `created_at` (oldest first) — chronological conversation flow
- Todo: `completed, due_date, -created_at` — incomplete first, then by urgency
- Mantra: `order, created_at` — user-controlled ordering with stable fallback

**JSON fields:** GratitudeEntry.items and WeeklySummary.themes use `JSONField(default=list)`. Tests verify they round-trip as Python lists through the database, and that the default is an empty list (not None).

### TDD moment
All 41 new tests passed on the first run after writing the models. This might seem like "the tests didn't catch anything" — but the real value was that writing the tests first forced every design decision to be explicit. The ordering, the constraints, the defaults, the field types — all decided in the test file before a single line of model code was written. The model code was just transcription of decisions already made.

---

## 2026-02-01 — REST API Layer (TDD) `#tdd` `#architecture`

### What happened
- Wrote 52 new API tests BEFORE writing any serializer/viewset code
- Implemented serializers, viewsets, URL routing for all endpoints
- Fixed 2 categories of test failures, then all 107 tests green

### Endpoints implemented

| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/api/auth/me/` | GET, PATCH | Current user profile |
| `/api/journal/` | GET, POST | List/create journal entries |
| `/api/journal/today/` | GET | Today's entry |
| `/api/journal/{date}/` | GET | Entry by date |
| `/api/journal/{id}/` | PATCH | Update entry |
| `/api/checkins/today/` | GET | Today's checkin (auto-creates) |
| `/api/checkins/meditation/` | POST | Log meditation |
| `/api/gratitude/` | GET, POST | List/create gratitude |
| `/api/gratitude/today/` | GET | Today's gratitude |
| `/api/todos/` | GET, POST | List/create todos |
| `/api/todos/{id}/` | PATCH, DELETE | Update/delete todo |
| `/api/todos/{id}/complete/` | POST | Mark todo complete |
| `/api/mantras/` | GET, POST | List/create mantras |
| `/api/mantras/{id}/` | PATCH, DELETE | Update/delete mantra |
| `/api/mantras/reorder/` | POST | Reorder mantras |

### What the tests caught

**Pagination missing:** Tests expected `response.data["results"]` (paginated format) but got a plain list. The test forced us to configure `DEFAULT_PAGINATION_CLASS` in DRF settings. Without the test, we might not have noticed until the frontend was built.

**Date auto-defaulting broken:** Tests for `POST /api/journal/` without a `date` field returned 400. DRF's ModelSerializer makes `date` required because the model field doesn't allow blank/null. The test forced us to explicitly declare `date = DateField(required=False, default=None)` on the serializer with auto-defaulting in `create()`.

**Security test: `test_cannot_set_arbitrary_fields`:** Proved that users can't escalate privileges via `PATCH /api/auth/me/` with `{"is_superuser": true}`. The UserSerializer's explicit `fields` list + `read_only_fields` prevent this — but the test proves it.

### Multi-tenancy at HTTP level
Every resource has at least one test proving user isolation:
- List endpoints return 0 results for other users' data
- Detail endpoints return 404 (not 403) for other users' resources — don't even reveal existence
- Complete/delete actions on other users' resources return 404

### Key pattern
```python
# Every viewset follows this pattern — user scoping via get_queryset
def get_queryset(self):
    return Model.objects.filter(user=self.request.user)
```
This single line, repeated in every viewset, is what the multi-tenancy tests enforce.

---

<!-- New entries will be added above this line -->
