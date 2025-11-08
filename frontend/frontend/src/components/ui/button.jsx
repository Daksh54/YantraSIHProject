import * as React from "react";
import { cn } from "../../lib/utils";

export function Button({ className, variant = "default", ...props }) {
  const base =
    "inline-flex items-center justify-center rounded-2xl px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50";
  const variants = {
    default: "bg-[#345a70] text-[#f0daad] hover:bg-[#1d3d59]",
    outline: "border border-gray-400 text-gray-700 hover:bg-gray-100",
  };
  return (
    <button className={cn(base, variants[variant], className)} {...props} />
  );
}
