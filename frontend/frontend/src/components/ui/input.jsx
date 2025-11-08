import * as React from "react";
import { cn } from "../../lib/utils";

export const Input = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-md border border-gray-400 bg-[#f0daad] text-black text-[#264f73]px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#264f73]",
        className
      )}
      {...props}
    />
  );
});
Input.displayName = "Input";
