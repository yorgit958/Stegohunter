import { useLocation } from "react-router-dom";
import { Shield, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const pageNames: Record<string, string> = {
  "/scan": "Image Scanner",
  "/dnn": "DNN Analyzer",
  "/neutralize": "Threat Neutralization",
  "/reports": "Reports",
  "/admin": "Admin Panel",
};

export default function ComingSoon() {
  const location = useLocation();
  const name = pageNames[location.pathname] || "This Page";

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
      <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center">
        <Shield className="h-8 w-8 text-primary" />
      </div>
      <div className="space-y-2">
        <h1 className="text-2xl font-bold">{name}</h1>
        <p className="text-muted-foreground max-w-md">
          This module is under active development and will be available in a future release.
        </p>
      </div>
      <Link to="/dashboard">
        <Button variant="outline" className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Button>
      </Link>
    </div>
  );
}
