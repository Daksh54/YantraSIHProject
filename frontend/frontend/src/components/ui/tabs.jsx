import * as React from "react";

export function Tabs({ defaultValue, children }) {
  const [active, setActive] = React.useState(defaultValue);
  return (
    <div>
      {React.Children.map(children, (child) =>
        React.cloneElement(child, { active, setActive })
      )}
    </div>
  );
}

export function TabsList({ children, className }) {
  return (
    <div className={`flex gap-2 p-2 rounded-md ${className}`}>{children}</div>
  );
}

export function TabsTrigger({ value, children, active, setActive }) {
  return (
    <button
      onClick={() => setActive(value)}
      className={`px-3 py-1 rounded-md text-sm ${
        active === value ? "bg-[#345a70] text-white" : "bg-gray-200"
      }`}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, active, children, className }) {
  if (active !== value) return null;
  return <div className={className}>{children}</div>;
}
