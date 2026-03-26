import { Link } from "react-router-dom";
import { Shield, ArrowLeft, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="text-center space-y-6">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-threat/10 mx-auto">
          <AlertTriangle className="h-8 w-8 text-threat" />
        </div>
        <div>
          <h1 className="text-5xl font-bold text-primary glow-text mb-2">404</h1>
          <p className="text-lg text-muted-foreground">Access Denied — Route not found</p>
          <p className="text-sm text-muted-foreground/60 font-mono mt-1">ERR_ROUTE_NOT_FOUND</p>
        </div>
        <Link to="/">
          <Button variant="outline" className="gap-2">
            <ArrowLeft className="h-4 w-4" /> Return to Base
          </Button>
        </Link>
      </div>
    </div>
  );
}
