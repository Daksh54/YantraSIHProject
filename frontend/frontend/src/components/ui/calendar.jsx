import React from "react";

export function Calendar({ selected, onSelect, className }) {
  return (
    <input
      type="date"
      value={selected.toISOString().split("T")[0]}
      onChange={(e) => onSelect(new Date(e.target.value))}
      className={`w-full h-10 rounded-md border border-gray-400 bg-[#f0daad] text-black px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#264f73] ${className}`}
    />
  );
}
export function TimePicker({ selected, onSelect, className }) {
  return (
    <input
      type="time"
      value={selected.toISOString().split("T")[0]}
      onChange={(e) => onSelect(new TimeRanges(e.target.value))}
      className={`w-full h-10 rounded-md border border-gray-400 bg-[#f0daad] text-black px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#264f73] ${className}`}
    />
  );
}
