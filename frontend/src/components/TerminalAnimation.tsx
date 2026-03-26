import { useState, useEffect } from "react";

const scanLines = [
  { text: "$ stego-hunter scan --target suspicious_image.png", delay: 0, color: "text-primary" },
  { text: "[INFO] Loading image... (2.4 MB)", delay: 800, color: "text-muted-foreground" },
  { text: "[SCAN] Extracting LSB bit planes...", delay: 1600, color: "text-muted-foreground" },
  { text: "[SCAN] Analyzing pixel distribution entropy...", delay: 2400, color: "text-muted-foreground" },
  { text: "[SCAN] Running CNN classifier (ResNet-50)...", delay: 3200, color: "text-muted-foreground" },
  { text: "[SCAN] Checking YARA rule signatures...", delay: 4000, color: "text-muted-foreground" },
  { text: "[████████████████████████████████] 100%", delay: 4800, color: "text-primary" },
  { text: "", delay: 5200, color: "" },
  { text: "⚠ THREAT DETECTED — Payload found in LSB channel", delay: 5600, color: "text-threat" },
  { text: "  ├─ Type: Embedded executable (PE32)", delay: 6000, color: "text-threat" },
  { text: "  ├─ Size: 48.2 KB hidden payload", delay: 6400, color: "text-threat" },
  { text: "  ├─ YARA Match: rule.StegoMalware_PE_LSB", delay: 6800, color: "text-warning" },
  { text: "  └─ Confidence: 99.2%", delay: 7200, color: "text-safe" },
  { text: "", delay: 7600, color: "" },
  { text: "[ACTION] Ready to neutralize. Run: stego-hunter neutralize --id scan_7f3a", delay: 8000, color: "text-primary" },
];

export function TerminalAnimation() {
  const [visibleLines, setVisibleLines] = useState<number>(0);

  useEffect(() => {
    const timers = scanLines.map((line, index) =>
      setTimeout(() => setVisibleLines(index + 1), line.delay)
    );

    const resetTimer = setTimeout(() => {
      setVisibleLines(0);
      // Restart after a pause
      const restartTimers = scanLines.map((line, index) =>
        setTimeout(() => setVisibleLines(index + 1), line.delay + 1000)
      );
      return () => restartTimers.forEach(clearTimeout);
    }, 10000);

    return () => {
      timers.forEach(clearTimeout);
      clearTimeout(resetTimer);
    };
  }, []);

  return (
    <div className="glass-card glow-border rounded-lg overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border/50">
        <div className="w-3 h-3 rounded-full bg-threat/80" />
        <div className="w-3 h-3 rounded-full bg-warning/80" />
        <div className="w-3 h-3 rounded-full bg-safe/80" />
        <span className="ml-2 text-xs text-muted-foreground font-mono">stego-hunter — scan</span>
      </div>
      <div className="p-4 font-mono text-sm leading-relaxed h-[340px] overflow-hidden">
        {scanLines.slice(0, visibleLines).map((line, i) => (
          <div key={i} className={`${line.color} ${line.text === "" ? "h-4" : ""}`}>
            {line.text}
          </div>
        ))}
        {visibleLines < scanLines.length && (
          <span className="terminal-cursor text-primary">▊</span>
        )}
      </div>
    </div>
  );
}
