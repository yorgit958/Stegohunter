import React, { useEffect, useState } from "react";
import { adminApi } from "../lib/api";
import { useAuthStore } from "../store/authStore";
import { Link } from "react-router-dom";
import {
    Shield, Users, ScanSearch, Activity, ShieldAlert, ShieldCheck,
    Server, Loader2, AlertTriangle, CheckCircle2, XCircle,
    BarChart3, BrainCircuit, RefreshCw, Lock
} from "lucide-react";

function StatCard({ icon: Icon, label, value, sublabel, color = "primary" }: { icon: any; label: string; value: string | number; sublabel?: string; color?: string }) {
    const colorMap: Record<string, string> = {
        primary: "text-primary bg-primary/10 border-primary/20",
        red: "text-red-400 bg-red-500/10 border-red-500/20",
        green: "text-green-400 bg-green-500/10 border-green-500/20",
        yellow: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
        blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    };
    const c = colorMap[color] || colorMap.primary;

    return (
        <div className="bg-black/40 border border-white/5 rounded-xl p-5 hover:border-white/10 transition-all group">
            <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] uppercase font-bold tracking-widest text-white/40">{label}</span>
                <div className={`p-2 rounded-lg ${c}`}>
                    <Icon className="w-4 h-4" />
                </div>
            </div>
            <div className="text-3xl font-black text-white tracking-tight">{value}</div>
            {sublabel && <p className="text-xs text-white/30 mt-1">{sublabel}</p>}
        </div>
    );
}

function ServiceStatus({ name, status }: { name: string; status: string }) {
    const iconMap: Record<string, JSX.Element> = {
        online: <CheckCircle2 className="w-4 h-4 text-green-400" />,
        offline: <XCircle className="w-4 h-4 text-red-400" />,
        degraded: <AlertTriangle className="w-4 h-4 text-yellow-400" />,
        unknown: <Loader2 className="w-4 h-4 text-white/30 animate-spin" />,
    };
    const statusColors: Record<string, string> = {
        online: "text-green-400",
        offline: "text-red-400",
        degraded: "text-yellow-400",
        unknown: "text-white/30",
    };
    const bgColors: Record<string, string> = {
        online: "bg-green-500/5 border-green-500/20",
        offline: "bg-red-500/5 border-red-500/20",
        degraded: "bg-yellow-500/5 border-yellow-500/20",
        unknown: "bg-white/5 border-white/10",
    };

    return (
        <div className={`flex items-center justify-between p-4 rounded-lg border ${bgColors[status] || bgColors.unknown}`}>
            <div className="flex items-center gap-3">
                <Server className="w-4 h-4 text-white/50" />
                <span className="text-sm font-medium text-white capitalize">{name.replace(/_/g, " ")}</span>
            </div>
            <div className="flex items-center gap-2">
                {iconMap[status] || iconMap.unknown}
                <span className={`text-xs font-semibold uppercase tracking-wider ${statusColors[status] || statusColors.unknown}`}>
                    {status}
                </span>
            </div>
        </div>
    );
}

function ThreatBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
    const pct = total > 0 ? (count / total) * 100 : 0;
    return (
        <div className="space-y-1">
            <div className="flex justify-between text-xs">
                <span className="text-white/60 capitalize">{label}</span>
                <span className="text-white font-mono">{count}</span>
            </div>
            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

export default function AdminPage() {
    const { user } = useAuthStore();
    const [stats, setStats] = useState<any>(null);
    const [health, setHealth] = useState<any>(null);
    const [users, setUsers] = useState<any[]>([]);
    const [recentScans, setRecentScans] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    // Frontend role guard — non-admins see an access denied screen
    if (user?.role !== "admin") {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4">
                <div className="p-4 rounded-full bg-red-500/10 border border-red-500/20">
                    <Lock className="w-10 h-10 text-red-400" />
                </div>
                <h1 className="text-2xl font-bold text-white">Access Denied</h1>
                <p className="text-white/50 max-w-md">You need administrator privileges to access this page. Contact your system admin for elevated access.</p>
                <Link to="/dashboard" className="text-primary hover:underline text-sm mt-2">← Back to Dashboard</Link>
            </div>
        );
    }

    const fetchData = async () => {
        try {
            const [statsRes, healthRes, usersRes, scansRes] = await Promise.all([
                adminApi.getSystemStats(),
                adminApi.getServiceHealth(),
                adminApi.getUsers(),
                adminApi.getRecentScans(8),
            ]);
            setStats(statsRes);
            setHealth(healthRes);
            setUsers(usersRes.users || []);
            setRecentScans(scansRes.scans || []);
        } catch (err) {
            console.error("Admin data fetch error:", err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => { fetchData(); }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchData();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
        );
    }

    const s = stats?.scans || {};
    const t = stats?.threats || {};
    const u = stats?.users || {};
    const n = stats?.neutralization || {};
    const levels = t.levels || {};

    return (
        <div className="space-y-8 container mx-auto max-w-7xl py-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                        <Shield className="w-8 h-8 text-primary" />
                        Admin Control Center
                    </h1>
                    <p className="text-white/50 mt-1">System-wide monitoring, user management, and service health.</p>
                </div>
                <button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 text-primary rounded-lg text-sm font-medium hover:bg-primary/20 transition-colors disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
                    Refresh
                </button>
            </div>

            {/* Top Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                <StatCard icon={ScanSearch} label="Total Scans" value={s.total || 0} sublabel={`${s.completed || 0} completed`} />
                <StatCard icon={ShieldAlert} label="Threats Found" value={t.total_detected || 0} color="red" sublabel={`${levels.critical || 0} critical`} />
                <StatCard icon={ShieldCheck} label="Clean Files" value={t.clean || 0} color="green" />
                <StatCard icon={Users} label="Users" value={u.total || 0} color="blue" sublabel={`${u.active || 0} active`} />
                <StatCard icon={Activity} label="Neutralized" value={n.total_neutralized || 0} color="yellow" />
                <StatCard icon={BrainCircuit} label="DNN Scans" value={s.dnn_scans || 0} sublabel={`${s.total_data_processed_mb || 0} MB processed`} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Threat Distribution */}
                <div className="bg-black/40 border border-white/5 rounded-xl p-6 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="w-5 h-5 text-primary" />
                        <h2 className="font-semibold text-white">Threat Distribution</h2>
                    </div>
                    <div className="space-y-3">
                        <ThreatBar label="Critical" count={levels.critical || 0} total={t.total_detected + t.clean || 1} color="bg-red-500" />
                        <ThreatBar label="High" count={levels.high || 0} total={t.total_detected + t.clean || 1} color="bg-orange-500" />
                        <ThreatBar label="Medium" count={levels.medium || 0} total={t.total_detected + t.clean || 1} color="bg-yellow-500" />
                        <ThreatBar label="Low" count={levels.low || 0} total={t.total_detected + t.clean || 1} color="bg-blue-500" />
                        <ThreatBar label="Clean" count={t.clean || 0} total={t.total_detected + t.clean || 1} color="bg-green-500" />
                    </div>
                </div>

                {/* Service Health */}
                <div className="bg-black/40 border border-white/5 rounded-xl p-6 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Server className="w-5 h-5 text-primary" />
                        <h2 className="font-semibold text-white">Service Health</h2>
                    </div>
                    <div className="space-y-3">
                        {health?.services && Object.entries(health.services).map(([name, info]: [string, any]) => (
                            <ServiceStatus key={name} name={name} status={info.status} />
                        ))}
                    </div>
                </div>

                {/* Registered Users */}
                <div className="bg-black/40 border border-white/5 rounded-xl p-6 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Users className="w-5 h-5 text-primary" />
                        <h2 className="font-semibold text-white">User Management</h2>
                    </div>
                    <div className="space-y-2 max-h-[320px] overflow-y-auto">
                        {users.length === 0 ? (
                            <p className="text-white/30 text-sm text-center py-6">No users found</p>
                        ) : (
                            users.map((user: any) => (
                                <div key={user.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${user.role === "admin" ? "bg-yellow-500/20 text-yellow-400" : "bg-primary/20 text-primary"}`}>
                                            {(user.username || "?").charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-white">{user.username}</p>
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${user.role === "admin" ? "bg-yellow-500/10 text-yellow-400" : "bg-blue-500/10 text-blue-400"}`}>
                                                {user.role}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className={`w-2 h-2 rounded-full ${user.is_active ? "bg-green-400" : "bg-red-400"}`} />
                                        <button
                                            onClick={async (e) => {
                                                e.stopPropagation();
                                                const newRole = user.role === "admin" ? "analyst" : "admin";
                                                const confirmText = user.role === "admin"
                                                    ? `Demote ${user.username} to analyst?`
                                                    : `Promote ${user.username} to admin?`;
                                                if (!window.confirm(confirmText)) return;
                                                try {
                                                    await adminApi.updateUserRole(user.id, newRole);
                                                    setUsers(prev => prev.map(u => u.id === user.id ? { ...u, role: newRole } : u));
                                                } catch (err: any) {
                                                    alert(err.response?.data?.detail || "Failed to update role");
                                                }
                                            }}
                                            className={`text-[10px] font-semibold px-2.5 py-1 rounded border transition-colors ${
                                                user.role === "admin"
                                                    ? "border-red-500/30 text-red-400 hover:bg-red-500/10"
                                                    : "border-green-500/30 text-green-400 hover:bg-green-500/10"
                                            }`}
                                        >
                                            {user.role === "admin" ? "Demote" : "Promote"}
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* Recent System-Wide Scans */}
            <div className="bg-black/40 border border-white/5 rounded-xl overflow-hidden">
                <div className="p-5 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <ScanSearch className="w-5 h-5 text-primary" />
                        <h2 className="font-semibold text-white">Recent System-Wide Scans</h2>
                    </div>
                    <span className="text-xs text-white/30 uppercase">All Users</span>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/5">
                                <th className="text-left px-5 py-3 text-[10px] uppercase font-bold tracking-widest text-white/30">File</th>
                                <th className="text-left px-5 py-3 text-[10px] uppercase font-bold tracking-widest text-white/30">Type</th>
                                <th className="text-left px-5 py-3 text-[10px] uppercase font-bold tracking-widest text-white/30">Status</th>
                                <th className="text-left px-5 py-3 text-[10px] uppercase font-bold tracking-widest text-white/30">Verdict</th>
                                <th className="text-right px-5 py-3 text-[10px] uppercase font-bold tracking-widest text-white/30">Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentScans.length === 0 ? (
                                <tr><td colSpan={5} className="text-center py-8 text-white/20">No scans recorded yet</td></tr>
                            ) : (
                                recentScans.map((scan: any) => (
                                    <tr key={scan.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                        <td className="px-5 py-3 text-sm text-white max-w-[200px] truncate">{scan.file_name}</td>
                                        <td className="px-5 py-3 text-xs text-white/40">{scan.job_type}</td>
                                        <td className="px-5 py-3">
                                            <span className={`text-xs font-medium px-2 py-1 rounded ${
                                                scan.status === "completed" ? "bg-green-500/10 text-green-400" :
                                                scan.status === "failed" ? "bg-red-500/10 text-red-400" :
                                                "bg-yellow-500/10 text-yellow-400"
                                            }`}>{scan.status}</span>
                                        </td>
                                        <td className="px-5 py-3">
                                            {scan.is_stego === null ? (
                                                <span className="text-xs text-white/20">—</span>
                                            ) : scan.is_stego ? (
                                                <span className="text-xs font-bold text-red-400 flex items-center gap-1">
                                                    <ShieldAlert className="w-3 h-3" />
                                                    {(scan.threat_level || "threat").toUpperCase()}
                                                </span>
                                            ) : (
                                                <span className="text-xs font-bold text-green-400 flex items-center gap-1">
                                                    <ShieldCheck className="w-3 h-3" />
                                                    CLEAN
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-5 py-3 text-xs text-white/30 text-right whitespace-nowrap">
                                            {new Date(scan.created_at).toLocaleString()}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
