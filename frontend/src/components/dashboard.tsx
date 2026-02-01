"use client";

import { Chat } from "@/components/chat/chat";
import { MantrasPanel } from "@/components/panels/mantras-panel";
import { TodayPanel } from "@/components/panels/today-panel";
import { TodosPanel } from "@/components/panels/todos-panel";

export function Dashboard() {
  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col lg:flex-row">
      {/* Chat — primary interface */}
      <div className="flex-1 min-h-0 lg:border-r lg:border-border">
        <Chat />
      </div>

      {/* Side panels */}
      <div className="flex flex-col gap-3 overflow-y-auto border-t border-border p-3 lg:w-80 lg:border-t-0 xl:w-96">
        <TodayPanel />
        <TodosPanel />
        <MantrasPanel />
      </div>
    </div>
  );
}
