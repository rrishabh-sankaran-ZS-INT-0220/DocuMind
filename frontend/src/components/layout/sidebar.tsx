"use client";

import React from "react";
import { useAuth } from "@/context/auth-context";
import { useCollections, useQASessions } from "@/lib/hooks";
import {
  MessageSquare,
  Search,
  NotebookPen,
  FolderKanban,
  Hash,
  Clock,
} from "lucide-react";

interface SidebarProps {
  activeSessionId: string | null;
  onSelectSession: (sessionId: string | null) => void;
  onNewChat?: () => void;
  collapsed?: boolean;
}

export default function Sidebar({
  activeSessionId,
  onSelectSession,
  onNewChat,
  collapsed = false,
}: SidebarProps) {
  const { user } = useAuth();
  const { data: collections = [] } = useCollections();
  const { data: sessions = [] } = useQASessions();

  const userInitial =
    user?.email?.[0]?.toUpperCase() ??
    user?.full_name?.[0]?.toUpperCase() ??
    "U";

  const sidebarWidthClass = collapsed ? "w-[60px]" : "w-[260px]";

  return (
    <aside
      className={`${sidebarWidthClass} h-screen bg-[#0d0d0d] flex flex-col py-3 overflow-hidden text-foreground`}
      suppressHydrationWarning
    >
      {/* Logo row */}
      <div className="flex items-center gap-2.5 px-3 py-2 mb-1">
        <div className="w-9 h-9 rounded-full bg-white text-black text-[13px] font-bold flex items-center justify-center">
          D
        </div>
        {!collapsed && (
          <span className="text-[14px] font-semibold text-[#ececec]">
            DocuMind
          </span>
        )}
      </div>

      {/* Primary nav */}
      <div className="mt-2 space-y-1.5">
        <SidebarActionItem
          icon={MessageSquare}
          label="New Chat"
          collapsed={collapsed}
          onClick={() => {
            onNewChat?.();
            onSelectSession(null);
          }}
        />
        <SidebarActionItem
          icon={Search}
          label="Search"
          collapsed={collapsed}
          onClick={() => {}}
        />
        <SidebarActionItem
          icon={NotebookPen}
          label="Notes"
          collapsed={collapsed}
          onClick={() => {}}
        />
        <SidebarActionItem
          icon={FolderKanban}
          label="Workspace"
          collapsed={collapsed}
          onClick={() => {}}
        />
      </div>

      {/* Collections */}
      <div className="mt-4">
        {!collapsed && (
          <p className="px-3 pt-4 pb-1 text-[11px] font-semibold tracking-widest text-[#8a8a8a] uppercase">
            Collections
          </p>
        )}
        <div className="space-y-1">
          {collections.length === 0 && !collapsed && (
            <p className="px-3 py-1.5 text-[13px] text-[#8a8a8a]">
              No collections yet
            </p>
          )}
          {collections.map((collection) => (
            <button
              key={collection.id}
              type="button"
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-[14px] text-[#ececec] hover:bg-[#1f1f1f] cursor-pointer transition-colors duration-150"
            >
              <div className="w-7 h-7 rounded-md bg-[#1a1a1a] flex items-center justify-center text-[#ececec]">
                <Hash className="h-4 w-4" />
              </div>
              {!collapsed && (
                <span className="truncate">
                  {(collection as any).name ??
                    (collection as any).title ??
                    "Collection"}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Chats / sessions */}
      <div className="mt-4 flex-1">
        {!collapsed && (
          <p className="px-3 pt-4 pb-1 text-[11px] font-semibold tracking-widest text-[#8a8a8a] uppercase">
            Chats
          </p>
        )}
        <div className="space-y-1">
          {sessions.length === 0 && !collapsed && (
            <p className="px-3 py-1.5 text-[13px] text-[#8a8a8a]">
              No chats yet
            </p>
          )}
          {sessions.map((session, idx) => {
            const isActive = session.id === activeSessionId;
            return (
              <button
                key={session.id ?? idx}
                type="button"
                onClick={() => onSelectSession(session.id)}
                className={[
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-[14px] cursor-pointer transition-colors duration-150",
                  isActive
                    ? "bg-[#252525] text-white"
                    : "text-[#ececec] hover:bg-[#1f1f1f]",
                ].join(" ")}
                aria-selected={isActive}
              >
                <div className="w-7 h-7 rounded-md bg-[#1a1a1a] flex items-center justify-center text-[#ececec]">
                  <Clock className="h-4 w-4" />
                </div>
                {!collapsed && (
                  <span className="truncate">
                    {(session as any).title ??
                      (session as any).name ??
                      `Session ${idx + 1}`}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Bottom user card */}
      <div className="mt-auto pt-2 border-t border-[#2a2a2a]">
        <button
          type="button"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[#1f1f1f] cursor-pointer transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-indigo-500 text-white text-[13px] font-medium flex items-center justify-center">
            {userInitial}
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="truncate text-[14px] text-[#ececec]">
                {user?.full_name || user?.email || "Guest user"}
              </p>
              <p className="truncate text-[12px] text-[#8a8a8a]">
                {user ? user.email : "Not signed in"}
              </p>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
}

type SidebarActionItemProps = {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  collapsed: boolean;
  onClick: () => void;
};

function SidebarActionItem({
  icon: Icon,
  label,
  collapsed,
  onClick,
}: SidebarActionItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-3 px-3 py-2 rounded-lg text-[14px] text-[#ececec] hover:bg-[#1f1f1f] cursor-pointer transition-colors duration-150"
    >
      <Icon className="h-4 w-4" />
      {!collapsed && <span className="truncate">{label}</span>}
    </button>
  );
}