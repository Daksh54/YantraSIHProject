import * as React from "react";

export function Select({ value, onValueChange, children }) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        className="w-full h-10 rounded-md border border-gray-400 bg-[#f0daad] text-black px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#264f73]"
      >
        {children}
      </select>
    </div>
  );
}

export function SelectTrigger({ children }) {
  return children;
}
export function SelectValue({ placeholder }) {
  return <option value="">{placeholder}</option>;
}
export function SelectContent({ children }) {
  return children;
}
export function SelectItem({ value, children }) {
  return <option value={value}>{children}</option>;
}
