-- AI Personal Finance Coach — Database Schema

create extension if not exists "uuid-ossp";

-- Categories table (seeded with defaults)
create table categories (
  id uuid primary key default uuid_generate_v4(),
  name text not null unique,
  color text not null default '#6B7280',
  icon text not null default '💰',
  is_custom boolean not null default false,
  created_at timestamptz not null default now()
);

-- Transactions table
create table transactions (
  id uuid primary key default uuid_generate_v4(),
  date date not null,
  description text not null,
  amount numeric(12, 2) not null,
  merchant text,
  category_id uuid references categories(id) on delete set null,
  raw_csv_row jsonb,
  created_at timestamptz not null default now()
);

create index transactions_date_idx on transactions(date desc);
create index transactions_category_idx on transactions(category_id);

-- Budgets table
create table budgets (
  id uuid primary key default uuid_generate_v4(),
  category_id uuid not null references categories(id) on delete cascade,
  monthly_limit numeric(12, 2) not null,
  month_year text not null, -- format: "2024-01"
  created_at timestamptz not null default now(),
  unique(category_id, month_year)
);

-- Insights cache table (avoid re-generating AI insights on every page load)
create table insights_cache (
  id uuid primary key default uuid_generate_v4(),
  month_year text not null unique, -- format: "2024-01"
  content_json jsonb not null,
  generated_at timestamptz not null default now()
);

-- Seed default categories
insert into categories (name, color, icon) values
  ('Food & Dining', '#F59E0B', '🍔'),
  ('Transport', '#3B82F6', '🚗'),
  ('Shopping', '#8B5CF6', '🛍️'),
  ('Entertainment', '#EC4899', '🎬'),
  ('Health & Medical', '#10B981', '🏥'),
  ('Utilities', '#6B7280', '⚡'),
  ('Housing', '#EF4444', '🏠'),
  ('Travel', '#F97316', '✈️'),
  ('Subscriptions', '#14B8A6', '📺'),
  ('Education', '#6366F1', '📚'),
  ('Personal Care', '#A855F7', '💅'),
  ('Income', '#22C55E', '💵'),
  ('Transfers', '#94A3B8', '🔄'),
  ('Other', '#9CA3AF', '📦');
