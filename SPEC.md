# WuWei - Technical Specification

## Features

### 1. Conversational Interface (Primary)

The chat is the main UI. Users type naturally, the agent interprets intent and takes action.

**Supported intents:**
| User says | Agent action |
|-----------|--------------|
| "Did my meditation" / "Meditated for 20 min" | `log_meditation(duration_minutes=20)` |
| "Grateful for: X, Y, Z" | `save_gratitude_list(items=["X", "Y", "Z"])` |
| "Let me journal..." / longer text | `save_journal_entry(content="...")` → Reflect |
| "Remind me to X" / "Todo: X" | `create_todo(task="X", due_date=None)` |
| "Done with X" / "Finished X" | `complete_todo(search="X")` |
| "What are my todos?" | `get_todos()` |
| "What patterns have you noticed?" | `get_patterns()` |
| "Show me last week's entries" | `get_recent_entries(days=7)` |
| "What did I write about X?" | `search_entries(query="X")` |
| "Read my mantras" | `get_mantras()` |
| General conversation | Respond conversationally with Taoist lens |

### 2. Daily Check-ins

Auto-created each day at midnight (user's timezone) via Celery Beat:
- Meditation check-in (boolean + optional duration)
- Gratitude list (list of items)
- Journal entry (free text)

Dashboard shows completion status for today.

### 3. AI Reflection

After journal entries, the agent reflects back with:
- Acknowledgment of what was shared
- Taoist/therapeutic framing
- Pattern recognition (pulls from past entries via RAG)
- Gentle challenges or growth prompts when appropriate

### 4. Pattern Recognition

RAG-powered analysis:
- Retrieves semantically similar past entries
- Tracks recurring themes (sleep, anxiety, relationships, work)
- Notices cycles (time-of-month patterns, weekly patterns)
- Remembers commitments user made ("I'm going to set boundaries")

**Weekly summary job:** Celery Beat task runs weekly, generates a summary stored in the database. Agent can reference these for long-term patterns.

### 5. Todo Management

Simple task list:
- Create with optional due date
- Mark complete
- View pending todos
- Natural language parsing ("remind me tomorrow" → due_date = tomorrow)

### 6. Mantras

Static/editable reference section:
- User's personal mantras and reminders
- Displayed during meditation or on request
- Editable via settings or chat ("Add mantra: X")

### 7. Push Notifications (PWA)

Daily reminder to journal:
- Configurable time (default: 8pm)
- Uses Web Push API
- Can be disabled in settings

### 8. Data Export

Users can download their data:
- JSON export of all entries, gratitude lists, todos
- CSV export option

---

## Database Schema

### Users

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    timezone = models.CharField(max_length=50, default='America/New_York')
    daily_reminder_time = models.TimeField(default='20:00')
    reminder_enabled = models.BooleanField(default=True)
    anthropic_api_key = models.CharField(max_length=255, blank=True)  # Optional BYO key
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Rate limiting
    reflections_today = models.IntegerField(default=0)
    reflections_reset_date = models.DateField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

### Journal Entries

```python
class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    reflection = models.TextField(blank=True)  # AI response
    embedding = VectorField(dimensions=1536, null=True)  # pgvector
    date = models.DateField()  # The day this entry is for
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
```

### Daily Check-ins

```python
class DailyCheckin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Meditation
    meditation_completed = models.BooleanField(default=False)
    meditation_duration = models.IntegerField(null=True)  # minutes
    meditation_completed_at = models.DateTimeField(null=True)
    
    # Gratitude
    gratitude_completed = models.BooleanField(default=False)
    gratitude_completed_at = models.DateTimeField(null=True)
    
    # Journal
    journal_completed = models.BooleanField(default=False)
    journal_completed_at = models.DateTimeField(null=True)
    
    class Meta:
        unique_together = ['user', 'date']
```

### Gratitude Lists

```python
class GratitudeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    items = models.JSONField(default=list)  # ["item1", "item2", ...]
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']
```

### Todos

```python
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=500)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['completed', 'due_date', '-created_at']
```

### Mantras

```python
class Mantra(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
```

### Weekly Summaries

```python
class WeeklySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start = models.DateField()  # Monday of the week
    summary = models.TextField()  # AI-generated summary
    themes = models.JSONField(default=list)  # ["sleep", "work stress", ...]
    mood_trend = models.CharField(max_length=50, blank=True)  # "improving", "stable", "declining"
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'week_start']
```

### Chat Messages (for conversation history)

```python
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)  # 'user' or 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
```

---

## API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Email/password registration |
| POST | `/api/auth/login/` | Login, returns session |
| POST | `/api/auth/logout/` | Logout |
| POST | `/api/auth/google/` | Google OAuth callback |
| GET | `/api/auth/me/` | Current user info |
| PATCH | `/api/auth/me/` | Update user settings |

### Journal

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/journal/` | List entries (paginated) |
| GET | `/api/journal/today/` | Get today's entry |
| POST | `/api/journal/` | Create/update today's entry |
| GET | `/api/journal/{date}/` | Get entry by date |
| GET | `/api/journal/search/?q=` | Semantic search |

### Check-ins

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/checkins/today/` | Today's check-in status |
| POST | `/api/checkins/meditation/` | Log meditation |
| GET | `/api/checkins/history/` | Check-in history |

### Gratitude

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gratitude/` | List gratitude entries |
| GET | `/api/gratitude/today/` | Today's gratitude |
| POST | `/api/gratitude/` | Save today's gratitude |

### Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos/` | List todos |
| POST | `/api/todos/` | Create todo |
| PATCH | `/api/todos/{id}/` | Update todo |
| POST | `/api/todos/{id}/complete/` | Mark complete |
| DELETE | `/api/todos/{id}/` | Delete todo |

### Mantras

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/mantras/` | List mantras |
| POST | `/api/mantras/` | Create mantra |
| PATCH | `/api/mantras/{id}/` | Update mantra |
| DELETE | `/api/mantras/{id}/` | Delete mantra |
| POST | `/api/mantras/reorder/` | Reorder mantras |

### Chat (WebSocket)

| Type | Endpoint | Description |
|------|----------|-------------|
| WS | `/ws/chat/` | WebSocket for chat |

WebSocket message format:
```json
// Client → Server
{
  "type": "message",
  "content": "Did my meditation for 20 minutes"
}

// Server → Client (streaming)
{
  "type": "token",
  "content": "Great"
}

// Server → Client (complete)
{
  "type": "complete",
  "tool_calls": ["log_meditation"],
  "data": {"meditation_logged": true, "duration": 20}
}
```

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/json/` | Export all data as JSON |
| GET | `/api/export/csv/` | Export as CSV zip |

### Insights

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/insights/patterns/` | Get detected patterns |
| GET | `/api/insights/weekly/` | List weekly summaries |

---

## LangGraph Agent

### Graph Structure

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Classify   │
                    │   Intent    │
                    └──────┬──────┘
                           │
         ┌─────────┬───────┼───────┬─────────┐
         ▼         ▼       ▼       ▼         ▼
    ┌─────────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐
    │Meditation│ │Grat │ │Journ│ │Todo │ │ Query   │
    └────┬────┘ └──┬──┘ └──┬──┘ └──┬──┘ └────┬────┘
         │         │       │       │         │
         └─────────┴───────┼───────┴─────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Generate   │
                    │  Response   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    END      │
                    └─────────────┘
```

### Agent Tools

```python
@tool
def log_meditation(duration_minutes: Optional[int] = None) -> dict:
    """Log that the user completed their meditation.
    
    Args:
        duration_minutes: Optional duration in minutes
        
    Returns:
        Confirmation with today's check-in status
    """
    
@tool
def save_gratitude_list(items: List[str]) -> dict:
    """Save the user's gratitude list for today.
    
    Args:
        items: List of things the user is grateful for
        
    Returns:
        Confirmation with saved items
    """

@tool
def save_journal_entry(content: str) -> dict:
    """Save a journal entry for today. This will trigger an AI reflection.
    
    Args:
        content: The journal entry content
        
    Returns:
        Confirmation that entry was saved
    """

@tool
def create_todo(task: str, due_date: Optional[str] = None) -> dict:
    """Create a new todo item.
    
    Args:
        task: The task description
        due_date: Optional due date (YYYY-MM-DD format, or "today", "tomorrow")
        
    Returns:
        The created todo
    """

@tool
def complete_todo(search: str) -> dict:
    """Mark a todo as complete by searching for it.
    
    Args:
        search: Text to search for in todo tasks
        
    Returns:
        Confirmation or list of matches if ambiguous
    """

@tool
def get_todos(include_completed: bool = False) -> dict:
    """Get the user's todo list.
    
    Args:
        include_completed: Whether to include completed todos
        
    Returns:
        List of todos
    """

@tool
def get_recent_entries(days: int = 7) -> dict:
    """Get recent journal entries.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of recent entries with dates
    """

@tool
def search_entries(query: str, limit: int = 5) -> dict:
    """Semantic search over past journal entries.
    
    Args:
        query: What to search for
        limit: Max results to return
        
    Returns:
        Relevant past entries
    """

@tool
def get_patterns() -> dict:
    """Analyze patterns across the user's journal entries.
    
    Returns:
        Detected patterns, recurring themes, and insights
    """

@tool
def get_mantras() -> dict:
    """Get the user's mantras/reminders.
    
    Returns:
        List of mantras
    """

@tool
def add_mantra(content: str) -> dict:
    """Add a new mantra.
    
    Args:
        content: The mantra text
        
    Returns:
        Confirmation
    """

@tool
def get_todays_status() -> dict:
    """Get today's check-in status and overview.
    
    Returns:
        Meditation, gratitude, journal completion status
    """
```

### System Prompt (AI Personality)

```
You are a mindful companion rooted in Taoist philosophy. Your role is to support the user's daily practice of self-reflection, growth, and presence.

## Your Approach

**Taoist Lens:**
- Embrace Wu Wei (effortless action) — don't force insights, let them emerge naturally
- See challenges as part of the natural flow, not problems to fix
- Value simplicity and returning to one's authentic nature
- Recognize that opposites contain each other (yin/yang)

**Therapeutic Style:**
- Listen deeply and reflect back what you hear
- Ask questions that invite deeper exploration
- Notice patterns without judgment
- Validate emotions while gently offering perspective

**Coaching Element:**
- Remember commitments the user has made
- Gently hold them accountable ("You mentioned wanting to set boundaries...")
- Celebrate small wins and progress
- Offer concrete next steps when appropriate

**Tone:**
- Warm but not saccharine
- Direct but kind
- Wise but not preachy
- Conversational, not clinical

## Behavior Guidelines

1. **For simple commands** (logging meditation, creating todos): Be brief and confirming. Don't over-philosophize a checkbox.

2. **For journal entries**: Read carefully, reflect back key themes, offer a Taoist reframe if relevant, ask one thoughtful question or offer one gentle challenge.

3. **For pattern questions**: Pull from their history, be specific with examples, notice both struggles and growth.

4. **For emotional content**: Lead with empathy, validate before reframing, never minimize their experience.

5. **For gratitude lists**: Acknowledge briefly, perhaps note any themes, keep it light.

## What NOT to do

- Don't be preachy or lecture
- Don't offer unsolicited advice for simple check-ins
- Don't use excessive spiritual jargon
- Don't be artificially positive — acknowledge difficulty
- Don't make every response a teaching moment

## Memory Context

You have access to:
- Recent conversation history (current session)
- Tools to query past journal entries, patterns, and commitments
- Today's check-in status

Use this context to personalize responses and notice patterns, but don't be creepy about it.
```

---

## Scheduled Tasks (Celery Beat)

### Daily Check-in Creation
- **Schedule:** 00:01 in user's timezone
- **Action:** Create DailyCheckin record for each user

### Daily Reminder
- **Schedule:** User's configured reminder time
- **Action:** Send push notification if enabled

### Weekly Summary Generation
- **Schedule:** Sundays at 23:00 in user's timezone
- **Action:** Generate weekly summary from past 7 days of entries

### Rate Limit Reset
- **Schedule:** 00:00 UTC daily
- **Action:** Reset `reflections_today` counter for all users

---

## Frontend Pages

### `/login`
- Email/password form
- Google OAuth button
- Link to register

### `/register`
- Email/password registration
- Google OAuth option

### `/` (Dashboard)
Main page with everything visible:

```
┌─────────────────────────────────────────────────────────────────┐
│  WuWei                                 [Dashboard] [Settings] 👤│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                     CHAT                                │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │ User: Did my meditation for 15 minutes           │  │    │
│  │  │ WuWei: ✓ Logged. 15 minutes of stillness — the   │  │    │
│  │  │        water settles when we stop stirring.      │  │    │
│  │  │                                                   │  │    │
│  │  │ User: Grateful for: good sleep, my caregivers    │  │    │
│  │  │ WuWei: ✓ Saved. Rest and support — two gifts     │  │    │
│  │  │        worth noticing.                           │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │ Type a message...                            [→] │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐   │
│  │   TODAY     │ │   TODOS     │ │       MANTRAS           │   │
│  │             │ │             │ │                         │   │
│  │ ✓ Meditate  │ │ ☐ Call doc  │ │ • Intrusive thoughts    │   │
│  │ ✓ Gratitude │ │ ☐ Email X   │ │   are mud...            │   │
│  │ ☐ Journal   │ │             │ │ • There is no wasted    │   │
│  │             │ │             │ │   minute...             │   │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### `/history`
- Calendar view or list view toggle
- Click date to see that day's entry
- Search bar for semantic search

### `/insights`
- Pattern visualization
- Weekly summaries
- Theme tracking over time

### `/mantras`
- List of mantras
- Add/edit/delete/reorder

### `/settings`
- Profile info
- Timezone
- Reminder time
- Notification preferences
- API key (BYO)
- Data export buttons

---

## Testing Strategy

### Unit Tests

**Models:**
```python
def test_journal_entry_creates_embedding():
    entry = JournalEntry.objects.create(user=user, content="Test", date=today)
    assert entry.embedding is not None
    
def test_daily_checkin_auto_creates():
    # After Celery task runs
    assert DailyCheckin.objects.filter(user=user, date=today).exists()
```

**Agent Tools:**
```python
def test_log_meditation_updates_checkin():
    result = log_meditation(user, duration_minutes=20)
    checkin = DailyCheckin.objects.get(user=user, date=today)
    assert checkin.meditation_completed is True
    assert checkin.meditation_duration == 20

def test_search_entries_returns_relevant():
    # Create entries about sleep
    create_entry(user, "Couldn't sleep last night, anxious about work")
    create_entry(user, "Great day at the beach")
    
    results = search_entries(user, "sleep problems")
    assert "sleep" in results[0].content.lower()
```

### Integration Tests

**API:**
```python
def test_journal_create_requires_auth(client):
    response = client.post('/api/journal/', {'content': 'Test'})
    assert response.status_code == 401

def test_journal_create_success(auth_client):
    response = auth_client.post('/api/journal/', {'content': 'Test'})
    assert response.status_code == 201
    assert JournalEntry.objects.filter(user=user).exists()
```

**WebSocket:**
```python
async def test_chat_message_triggers_agent():
    communicator = WebsocketCommunicator(ChatConsumer, "/ws/chat/")
    connected, _ = await communicator.connect()
    assert connected
    
    await communicator.send_json_to({'type': 'message', 'content': 'Did my meditation'})
    response = await communicator.receive_json_from()
    assert response['type'] in ['token', 'complete']
```

### E2E Tests (Playwright)

```typescript
test('daily check-in flow', async ({ page }) => {
  await page.goto('/');
  await page.fill('[data-testid="chat-input"]', 'Did my meditation for 15 minutes');
  await page.click('[data-testid="send-button"]');
  
  await expect(page.locator('[data-testid="meditation-check"]')).toBeChecked();
});

test('journal entry with reflection', async ({ page }) => {
  await page.goto('/');
  await page.fill('[data-testid="chat-input"]', 'Let me journal about today. I felt anxious this morning...');
  await page.click('[data-testid="send-button"]');
  
  // Wait for streaming response
  await expect(page.locator('[data-testid="assistant-message"]')).toBeVisible();
  await expect(page.locator('[data-testid="journal-check"]')).toBeChecked();
});
```

---

## Data Import Script

```python
# scripts/import_trello.py

import json
from apps.journal.models import JournalEntry
from apps.mantras.models import Mantra
from apps.journal.models import GratitudeEntry

def import_trello(filepath: str, user):
    with open(filepath) as f:
        data = json.load(f)
    
    list_map = {lst['id']: lst['name'] for lst in data['lists']}
    
    for card in data['cards']:
        list_name = list_map.get(card['idList'], '')
        content = card.get('desc', '')
        
        if not content.strip():
            continue
            
        if 'Daily Personal Diary' in list_name:
            # Parse date from card
            date = parse_date(card)
            JournalEntry.objects.create(
                user=user,
                content=content,
                date=date
            )
            
        elif 'Gratitude' in list_name:
            date = parse_date(card)
            items = parse_gratitude_items(content)
            GratitudeEntry.objects.create(
                user=user,
                date=date,
                items=items
            )
            
        elif 'Mantras' in list_name:
            Mantra.objects.create(
                user=user,
                content=card.get('name', '') + '\n' + content
            )
```

---

## PWA Configuration

```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
});

module.exports = withPWA({
  // ... other config
});
```

```json
// public/manifest.json
{
  "name": "WuWei",
  "short_name": "WuWei",
  "description": "Mindful daily practice companion",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#16213e",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

---

## Security Considerations

- All API endpoints require authentication (except auth endpoints)
- User data strictly scoped by user ID
- API keys encrypted at rest
- Rate limiting on auth endpoints
- CORS configured for frontend domain only
- WebSocket connections authenticated via session
