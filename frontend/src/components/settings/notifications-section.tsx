"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { updateMe } from "@/lib/api/auth";

export function NotificationsSection() {
  const { user } = useAuth();
  const [enabled, setEnabled] = useState(user?.reminder_enabled ?? true);
  const [time, setTime] = useState(
    user?.daily_reminder_time?.slice(0, 5) ?? "20:00"
  );
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      await updateMe({
        reminder_enabled: enabled,
        daily_reminder_time: time + ":00",
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card title="Reminders">
      <form onSubmit={handleSave} className="space-y-4">
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
            className="h-4 w-4 rounded border-border accent-accent-primary"
          />
          <span className="text-sm text-text-primary">
            Daily journal reminder
          </span>
        </label>

        {enabled && (
          <div>
            <label className="text-sm text-text-secondary">Reminder time</label>
            <input
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-bg-primary px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-primary"
            />
          </div>
        )}

        <div className="flex items-center gap-3">
          <Button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
          {saved && (
            <span className="text-sm text-success">Saved</span>
          )}
        </div>
      </form>
    </Card>
  );
}
