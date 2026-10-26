-- Socratic AI: tables for saved sessions and transcripts.
-- Paste all of this into Supabase > SQL Editor and press Run, once.
-- Only the server (with the secret key) can read or write these tables.
-- RLS is on with no policies, and the public roles get no access, so the
-- browser and strangers cannot reach learner data through the API.

create table if not exists public.sessions (
  id         uuid primary key,          -- the session id the app makes
  data       jsonb not null,            -- the whole session, same as sessions/<id>.json
  updated_at timestamptz not null default now()
);

create table if not exists public.transcript_lines (
  id         bigint generated always as identity primary key,
  session_id uuid not null,             -- one line per turn, same as transcripts/<id>.jsonl
  line       jsonb not null,
  created_at timestamptz not null default now()
);

-- Reading one session's transcript in order, for the thesis export.
create index if not exists transcript_lines_session_idx
  on public.transcript_lines (session_id, id);

alter table public.sessions enable row level security;
alter table public.transcript_lines enable row level security;

revoke all on table public.sessions, public.transcript_lines from anon, authenticated;
grant select, insert, update, delete on table public.sessions, public.transcript_lines to service_role;

-- Signed-in learners (Sign in with Google, optional). Added 27 October 2026.
-- If the two tables above already exist, you can run just this part.
-- id is a one-way hash of the Google account id, so no name or email is stored.
-- data holds the learner's chat list, built topics and session and check ids.
create table if not exists public.profiles (
  id         text primary key,
  data       jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
revoke all on table public.profiles from anon, authenticated;
grant select, insert, update, delete on table public.profiles to service_role;
