// src/components/ui/Progress.js

import React from 'react';

export const Progress = ({ value, className }) => {
  return (
    <div className={`relative w-full h-6 bg-gray-200 rounded-full overflow-hidden ${className}`}>
      <div
        className="absolute left-0 top-0 h-full bg-indigo-600"
        style={{ width: `${value}%` }}
      ></div>
    </div>
  );
};
