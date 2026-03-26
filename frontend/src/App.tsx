import { useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuthStore } from "@/store/authStore";
import Index from "./pages/Index";
import DashboardPage from "./pages/DashboardPage";
import ComingSoon from "./pages/ComingSoon";
import Login from "./pages/Login";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";
import ProfilePage from "./pages/ProfilePage";
import ScanPage from "./pages/ScanPage";
import ScanResultPage from "./pages/ScanResultPage";
import NeutralizePage from "./pages/NeutralizePage";
import ReportsPage from "./pages/ReportsPage";
import DNNAnalysisPage from "./pages/DNNAnalysisPage";
import AdminPage from "./pages/AdminPage";

const queryClient = new QueryClient();

const App = () => {
  useEffect(() => {
    // Initialize Supabase Auth Session Listener on mount
    useAuthStore.getState().initialize().catch(console.error);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/scan" element={<ScanPage />} />
                <Route path="/scan/results/:id" element={<ScanResultPage />} />
                <Route path="/dnn-analysis" element={<DNNAnalysisPage />} />
                <Route path="/neutralize" element={<NeutralizePage />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/admin" element={<AdminPage />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
