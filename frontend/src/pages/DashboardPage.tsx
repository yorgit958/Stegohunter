import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    ScanSearch,
    Brain,
    ShieldCheck,
    ShieldAlert,
    Activity,
    ArrowRight,
    Loader2,
} from "lucide-react";
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
} from "recharts";
import { scanApi } from "../lib/api";


function StatusBadge({ status, isStego }: { status: string, isStego?: boolean }) {
    if (status !== "completed") return <Badge className="bg-warning/15 text-warning border-warning/30 hover:bg-warning/20">Pending</Badge>;
    if (isStego) return <Badge className="bg-threat/15 text-threat border-threat/30 hover:bg-threat/20">Infected</Badge>;
    return <Badge className="bg-safe/15 text-safe border-safe/30 hover:bg-safe/20">Clean</Badge>;
}

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [recentScans, setRecentScans] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [statsRes, jobsRes] = await Promise.all([
                    scanApi.getStats(),
                    scanApi.getJobs(5)
                ]);
                setStats(statsRes);
                setRecentScans(jobsRes.jobs || []);
            } catch (err) {
                console.error("Failed to fetch dashboard data:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
        );
    }

    // Prepare metrics
    const metrics = [
        { title: "Total Scans", value: stats?.total_scans || 0, icon: ScanSearch, color: "text-primary" },
        { title: "Threats Detected", value: stats?.threats_found || 0, icon: ShieldAlert, color: "text-threat" },
        { title: "Clean Files", value: stats?.clean || 0, icon: ShieldCheck, color: "text-safe" },
        { title: "Completed Scans", value: stats?.completed || 0, icon: Activity, color: "text-blue-400" },
    ];

    // Prepare pie chart data — always show a full scan breakdown
    const levels = stats?.threat_levels || {};
    const chartEntries = [
        { name: "Critical", value: levels.critical || 0, color: "#ef4444" },
        { name: "High",     value: levels.high || 0,     color: "#f97316" },
        { name: "Medium",   value: levels.medium || 0,   color: "#eab308" },
        { name: "Low",      value: levels.low || 0,      color: "#3b82f6" },
        { name: "Clean",    value: stats?.clean || 0,     color: "#22c55e" },
    ].filter(d => d.value > 0);

    const threatData = chartEntries.length > 0 
        ? chartEntries 
        : [{ name: "No Scans", value: 1, color: "#374151" }];

    const formatTimeAgo = (dateStr: string) => {
        const diffMs = new Date().getTime() - new Date(dateStr).getTime();
        const diffMins = Math.round(diffMs / 60000);
        if (diffMins < 60) return `${diffMins || 1} min ago`;
        const diffHrs = Math.round(diffMins / 60);
        if (diffHrs < 24) return `${diffHrs} hr ago`;
        return `${Math.round(diffHrs / 24)}d ago`;
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">Dashboard</h1>
                <p className="text-muted-foreground text-sm">System overview and recent scanning activity.</p>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {metrics.map((m) => (
                    <Card key={m.title} className="glass-card border-border/50">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-muted-foreground">{m.title}</CardTitle>
                            <m.icon className={`h-4 w-4 ${m.color}`} />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-white">{m.value}</div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Recent Activity */}
                <Card className="lg:col-span-2 glass-card border-border/50 flex flex-col">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-base text-white">Recent Scans</CardTitle>
                        <Link to="/reports" className="text-xs text-primary hover:underline">View All</Link>
                    </CardHeader>
                    <CardContent className="flex-1">
                        {recentScans.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-muted-foreground pt-10 pb-4">
                                <ScanSearch className="w-10 h-10 mb-3 opacity-20" />
                                <p>No scans performed yet.</p>
                                <Link to="/scan" className="text-primary hover:underline mt-2 text-sm">Run your first scan</Link>
                            </div>
                        ) : (
                            <Table>
                                <TableHeader>
                                    <TableRow className="border-border/30 hover:bg-transparent">
                                        <TableHead className="text-muted-foreground">ID</TableHead>
                                        <TableHead className="text-muted-foreground">File</TableHead>
                                        <TableHead className="text-muted-foreground">Status</TableHead>
                                        <TableHead className="text-muted-foreground text-right">Time</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {recentScans.map((scan) => {
                                        // A quick check if it's infected by looking at related results is hard since 
                                        // the Gateway GET /jobs just returns jobs without results payload embedded, 
                                        // but it's fine we'll guess from status for now, or just show 'Completed'.
                                        // Wait, to show infected/clean correctly on dashboard we need is_stego. 
                                        // Let's use the UI to link directly to results page.
                                        return (
                                            <TableRow 
                                                key={scan.id} 
                                                className="border-border/20 hover:bg-white/5 cursor-pointer"
                                                onClick={() => navigate(`/scan/results/${scan.id}`)}
                                            >
                                                <TableCell className="font-mono text-xs text-primary">{scan.id.substring(0, 8)}</TableCell>
                                                <TableCell className="font-medium text-xs text-white max-w-[150px] truncate" title={scan.file_name}>
                                                    {scan.file_name}
                                                </TableCell>
                                                <TableCell><StatusBadge status={scan.status} isStego={scan.is_stego} /></TableCell>
                                                <TableCell className="text-right text-xs text-muted-foreground">{formatTimeAgo(scan.created_at)}</TableCell>
                                            </TableRow>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        )}
                    </CardContent>
                </Card>
    
                {/* Threat Distribution */}
                <Card className="glass-card border-border/50">
                    <CardHeader>
                        <CardTitle className="text-base text-white">Threat Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={threatData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={50}
                                        outerRadius={75}
                                        paddingAngle={3}
                                        dataKey="value"
                                        stroke="none"
                                    >
                                        {threatData.map((entry, i) => (
                                            <Cell key={i} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        formatter={(val: number, name: string) => [`${val}`, name]}
                                        contentStyle={{
                                            backgroundColor: "#111827",
                                            border: "1px solid #374151",
                                            borderRadius: "8px",
                                            fontSize: "13px",
                                            color: "#fff",
                                        }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        {/* High-contrast legend */}
                        <div className="space-y-2 mt-3">
                            {threatData.map((d) => (
                                <div key={d.name} className="flex items-center justify-between px-3 py-2 rounded-lg" style={{ backgroundColor: `${d.color}15` }}>
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: d.color }} />
                                        <span className="text-sm text-white font-medium">{d.name}</span>
                                    </div>
                                    <span className="text-sm font-bold text-white">{d.value}</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Quick Actions */}
            <div className="grid sm:grid-cols-2 gap-4">
                <Card className="glass-card-hover border-border/50 cursor-pointer">
                    <Link to="/scan">
                        <CardContent className="p-6 flex items-center gap-4">
                            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                <ScanSearch className="h-6 w-6 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-white">Image Scanner</h3>
                                <p className="text-sm text-muted-foreground">Upload and analyze images for hidden payloads</p>
                            </div>
                            <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                        </CardContent>
                    </Link>
                </Card>
                <Card className="glass-card-hover border-border/50 cursor-pointer opacity-50">
                    <Link to="/dnn-analysis">
                        <CardContent className="p-6 flex items-center gap-4">
                            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                <Brain className="h-6 w-6 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-white">DNN Analyzer (Coming Soon)</h3>
                                <p className="text-sm text-muted-foreground">Scan neural networks for weight-based steganography</p>
                            </div>
                            <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                        </CardContent>
                    </Link>
                </Card>
            </div>
        </div>
    );
}
