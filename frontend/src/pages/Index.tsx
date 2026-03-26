import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Shield,
  ScanSearch,
  Brain,
  ShieldOff,
  FileCode,
  FileText,
  Activity,
  ArrowRight,
  ChevronRight,
} from "lucide-react";
import { TerminalAnimation } from "@/components/TerminalAnimation";
import { useAuthStore } from "@/store/authStore";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const features = [
  { icon: ScanSearch, title: "Image Scanning", desc: "Deep pixel-level analysis using LSB extraction, chi-square tests, and entropy mapping." },
  { icon: Brain, title: "DNN Analysis", desc: "Detect malicious payloads hidden within neural network weight matrices and checkpoints." },
  { icon: ShieldOff, title: "Threat Neutralization", desc: "Surgically remove embedded payloads while preserving image and model integrity." },
  { icon: FileCode, title: "YARA Rules", desc: "Custom rule engine for signature-based detection of known steganographic patterns." },
  { icon: FileText, title: "Integrity Reports", desc: "Detailed SSIM, PSNR, and MSE metrics with exportable forensic reports." },
  { icon: Activity, title: "Real-time Monitoring", desc: "Continuous scanning pipelines with webhook alerts and dashboard telemetry." },
];

const stats = [
  { value: "10M+", label: "Images Scanned" },
  { value: "99.7%", label: "Detection Rate" },
  { value: "< 2s", label: "Avg. Scan Time" },
  { value: "50K+", label: "Threats Neutralized" },
];

export default function Index() {
  const { user, isAuthenticated } = useAuthStore();
  
  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="border-b border-border/30 bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Shield className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold tracking-tight">
              Stego<span className="text-primary">Hunter</span>
            </span>
          </Link>
          <div className="flex items-center gap-3">
            {isAuthenticated && user ? (
              <Link to="/profile">
                <Button variant="ghost" className="relative h-8 w-8 rounded-full border border-border/50">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary/20 text-primary text-xs">
                      {user.username.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </Link>
            ) : (
              <Link to="/login">
                <Button variant="ghost" size="sm" className="text-muted-foreground">Sign In</Button>
              </Link>
            )}
            <Link to="/dashboard">
              <Button size="sm" className="gap-1">
                Dashboard <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/5 text-primary text-xs font-medium">
              <Activity className="h-3 w-3" /> Advanced Threat Detection
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.1] tracking-tight">
              Detect Hidden
              <br />
              <span className="text-primary glow-text">Steganographic</span>
              <br />
              Malware
            </h1>
            <p className="text-lg text-muted-foreground max-w-lg leading-relaxed">
              Uncover payloads concealed within images and deep neural network models.
              Enterprise-grade scanning powered by CNN classifiers and YARA signatures.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <Link to="/scan">
                <Button size="lg" className="gap-2 font-semibold">
                  <ScanSearch className="h-4 w-4" /> Start Scanning
                </Button>
              </Link>
              <Link to="/reports">
                <Button variant="outline" size="lg" className="gap-2">
                  View Documentation <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: "0.3s" }}>
            <TerminalAnimation />
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="border-y border-border/30 bg-secondary/20">
        <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((s) => (
            <div key={s.label} className="text-center space-y-1">
              <div className="text-3xl font-bold text-primary glow-text">{s.value}</div>
              <div className="text-sm text-muted-foreground">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Threat Explainer */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-12 space-y-3">
          <h2 className="text-3xl font-bold">The Invisible Threat</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Steganography hides malicious payloads inside ordinary-looking files.
            Traditional antivirus tools miss them entirely. StegoHunter doesn't.
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="glass-card-hover p-6 space-y-3">
            <ScanSearch className="h-8 w-8 text-primary" />
            <h3 className="text-lg font-semibold">Image Steganography</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Attackers embed executables, scripts, and C2 data within pixel values using LSB insertion,
              DCT coefficient manipulation, and adaptive encoding. Invisible to the naked eye.
            </p>
          </div>
          <div className="glass-card-hover p-6 space-y-3">
            <Brain className="h-8 w-8 text-primary" />
            <h3 className="text-lg font-semibold">DNN Model Steganography</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Malicious code is hidden within neural network weight matrices and checkpoint files.
              Models function normally while carrying concealed payloads in redundant parameters.
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-6 pb-20">
        <div className="text-center mb-12 space-y-3">
          <h2 className="text-3xl font-bold">Comprehensive Detection Suite</h2>
          <p className="text-muted-foreground">Six integrated modules for end-to-end stego analysis.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f) => (
            <div key={f.title} className="glass-card-hover p-6 space-y-3">
              <f.icon className="h-6 w-6 text-primary" />
              <h3 className="font-semibold">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border/30 bg-secondary/20">
        <div className="max-w-7xl mx-auto px-6 py-16 text-center space-y-6">
          <h2 className="text-3xl font-bold">Ready to Secure Your Assets?</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Start scanning images and DNN models for hidden threats in seconds.
          </p>
          <Link to="/scan">
            <Button size="lg" className="gap-2 font-semibold">
              <ScanSearch className="h-4 w-4" /> Launch Scanner
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/30">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Shield className="h-4 w-4 text-primary" />
            <span>StegoHunter © 2026</span>
          </div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link to="/dashboard" className="hover:text-foreground transition-colors">Dashboard</Link>
            <Link to="/scan" className="hover:text-foreground transition-colors">Scanner</Link>
            <Link to="/reports" className="hover:text-foreground transition-colors">Reports</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
