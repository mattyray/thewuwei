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

## 2026-02-01 — LangGraph Agent + Tools (TDD) `#tdd` `#langgraph` `#ai-pairing`

### What happened
- Wrote 31 agent tool tests BEFORE writing any tool code
- Implemented 10 agent tools as pure business logic functions
- Created system prompt with Taoist therapeutic personality
- Built LangGraph graph with tool orchestration (model → tools → model loop)
- All 138 tests passing (31 new + 107 existing)

### Tools implemented

| Tool | What it does | Key test |
|------|-------------|----------|
| `log_meditation` | Creates/updates DailyCheckin | Auto-creates checkin if missing |
| `save_gratitude_list` | Saves items, marks checkin | Replaces existing (not duplicates) |
| `save_journal_entry` | Saves entry, marks checkin | Appends to existing entry |
| `create_todo` | Creates with optional date | Parses "today"/"tomorrow" naturally |
| `complete_todo` | Fuzzy search + complete | Returns options if ambiguous |
| `get_todos` | Lists user's todos | Excludes completed by default |
| `get_recent_entries` | Journal entries by timeframe | Respects user scoping |
| `get_mantras` | Lists user's mantras | Ordered by user-defined order |
| `add_mantra` | Creates new mantra | Scoped to user |
| `get_todays_status` | Meditation/gratitude/journal | Isolated per user |

### Architecture decision: tools as pure functions

The tools are **not** LangChain `@tool` decorated functions that the LLM calls directly. Instead:

1. **Pure business logic** lives in `agent/tools.py` — plain Python functions that take a `user` and args, return dicts. These are what the tests exercise.
2. **LangChain tool wrappers** live in `agent/graph.py` — `@tool` decorated stubs that define the schema the LLM sees.
3. **The graph's `execute_tools` node** bridges them — it receives tool calls from the LLM, injects the `user` from config, and calls the real function.

This separation means:
- Tools are testable without mocking any LLM
- The LLM tool schema is decoupled from the implementation
- User injection happens in one place (the graph node), not scattered across tools

### TDD moments

**`test_complete_todo_ambiguous`:** This test forced the design of "what happens when 'call' matches both 'Call the doctor' and 'Call mom'?" Instead of guessing, the tool returns `{"matches": [...]}` so the agent can ask the user to clarify. The test drove an explicit UX decision.

**`test_save_journal_appends_to_existing`:** Should a second journal message overwrite or append? The test decided: **append**. The user might journal multiple times throughout the day, and we shouldn't lose the morning entry when they write in the evening.

**`test_create_todo_with_relative_date_tomorrow`:** Natural language date parsing ("tomorrow", "today") was tested before being implemented. The test defined the contract: `due_date="tomorrow"` → `date.today() + timedelta(days=1)`.

### 31/31 tool tests passed on first run
The pure function architecture paid off — with well-defined inputs and outputs, the implementation was straightforward transcription of the test contracts.

---

## 2026-02-01 — WebSocket Consumer + Celery Tasks (TDD) `#tdd` `#architecture` `#ai-pairing`

### What happened
- Wrote 6 WebSocket tests and 5 Celery task tests BEFORE implementation
- Implemented `ChatConsumer` (async WebSocket consumer with auth, persistence, agent bridge)
- Wired up ASGI routing with `AuthMiddlewareStack` + `URLRouter`
- Implemented 2 Celery tasks: `create_daily_checkins`, `reset_rate_limits`
- Hit async transaction isolation bug in tests, fixed, all 149 tests passing

### Tests written

| Test | What it proved |
|------|---------------|
| `test_authenticated_user_connects` | WebSocket accepts authenticated users |
| `test_unauthenticated_rejected` | AnonymousUser gets connection denied |
| `test_user_message_saved` | Sending a message persists to ChatMessage |
| `test_assistant_response_saved` | Both user + assistant messages saved (count=2) |
| `test_complete_message_includes_content` | Response includes type="complete" + content |
| `test_messages_scoped_to_user` | User A's messages don't appear in User B's history |
| `test_creates_checkins_for_all_users` | Daily task creates checkins for every active user |
| `test_does_not_duplicate_checkins` | Idempotent — won't create if one exists |
| `test_creates_for_inactive_check` | Only active users get checkins |
| `test_resets_reflection_count` | Rate limit counter resets to 0 |
| `test_updates_reset_date` | Reset date updates to today |

### Architecture: WebSocket consumer design

The `ChatConsumer` is thin — it handles auth, persistence, and response formatting. The actual intelligence lives in the LangGraph agent:

```
WebSocket message → save user message → call agent → save response → send back
```

Key design choice: `get_agent_response()` is a separate method specifically so tests can mock it. The real implementation calls `agent.invoke()` via `database_sync_to_async`, but tests replace it with a simple `AsyncMock(return_value="...")`. This lets us test the WebSocket plumbing without needing an LLM.

### TDD moment: async transaction isolation

**The bug:** Three WebSocket message tests failed with `UniqueViolation` — duplicate key on `users_user.email`. The standard `user` fixture creates `test@example.com`, but `database_sync_to_async` runs in a separate thread. Django's test transaction rollback doesn't cross thread boundaries, so users from one test leaked into the next.

**The fix the tests demanded:**
1. `pytestmark = pytest.mark.django_db(transaction=True)` — use real transactions with proper cleanup
2. UUID-based unique emails: `f"test-{uuid.uuid4().hex[:8]}@example.com"` — no collisions

This is a subtle Django Channels gotcha. Without TDD catching it early, this would have been a painful debugging session in a larger codebase. The failing test told us exactly what was wrong — the fix was mechanical.

### Celery tasks: simplicity wins

Both Celery tasks are intentionally simple:
- `create_daily_checkins`: Loop through active users, `get_or_create` for today. Idempotent by design.
- `reset_rate_limits`: Bulk `update()` — resets everyone at once. No per-user loop needed.

The test for inactive users (`test_creates_for_inactive_check`) drove the `.filter(is_active=True)` clause — without it, deactivated accounts would still get daily checkins.

---

<!-- New entries will be added above this line -->
