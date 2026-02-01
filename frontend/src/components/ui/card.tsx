interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, children, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-border bg-bg-secondary p-4 ${className}`}
    >
      {title && (
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-text-muted">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
