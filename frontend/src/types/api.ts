// Pagination wrapper (DRF PageNumberPagination)
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface User {
  id: number;
  email: string;
  timezone: string;
  daily_reminder_time: string | null;
  reminder_enabled: boolean;
  reflections_today: number;
  date_joined: string;
}

export interface JournalEntry {
  id: number;
  content: string;
  reflection: string;
  date: string; // YYYY-MM-DD
  created_at: string;
  updated_at: string;
}

export interface DailyCheckin {
  id: number;
  date: string;
  meditation_completed: boolean;
  meditation_duration: number | null;
  meditation_completed_at: string | null;
  gratitude_completed: boolean;
  gratitude_completed_at: string | null;
  journal_completed: boolean;
  journal_completed_at: string | null;
}

export interface GratitudeEntry {
  id: number;
  date: string;
  items: string[];
  created_at: string;
}

export interface Todo {
  id: number;
  task: string;
  due_date: string | null;
  completed: boolean;
  completed_at: string | null;
  created_at: string;
}

export interface Mantra {
  id: number;
  content: string;
  order: number;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface PersistedChatMessage extends ChatMessage {
  id: number;
  created_at: string;
}

export interface DailySummary {
  date: string; // YYYY-MM-DD
  checkin: DailyCheckin | null;
  journal: JournalEntry | null;
  gratitude: GratitudeEntry | null;
  todos: Todo[];
  chat_messages: PersistedChatMessage[];
}
