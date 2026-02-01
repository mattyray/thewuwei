import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost";

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-accent-primary text-white hover:bg-accent-primary/90 disabled:opacity-50",
  secondary:
    "bg-bg-tertiary text-text-primary hover:bg-bg-tertiary/80 disabled:opacity-50",
  ghost:
    "bg-transparent text-text-secondary hover:text-text-primary hover:bg-bg-secondary disabled:opacity-50",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  fullWidth?: boolean;
}

export function Button({
  variant = "primary",
  fullWidth = false,
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors cursor-pointer ${
        variantClasses[variant]
      } ${fullWidth ? "w-full" : ""} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
