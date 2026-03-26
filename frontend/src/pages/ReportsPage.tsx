import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Loader2, FileText, Search, ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react";
import { scanApi } from "../lib/api";

function ThreatBadge({ scan }: { scan: any }) {
    // If the scan hasn't completed analysis yet
    if (scan.status !== "completed") {
        return <Badge className="bg-yellow-500/15 text-yellow-400 border-yellow-500/30">Pending</Badge>;
    }
    
    // If there are no scan_results joined yet
    if (scan.is_stego === null || scan.is_stego === undefined) {
        return <Badge className="bg-gray-500/15 text-gray-400 border-gray-500/30"><ShieldQuestion className="w-3 h-3 mr-1" />Unknown</Badge>;
    }

    if (scan.is_stego) {
        const level = scan.threat_level || "high";
        if (level === "critical") {
            return <Badge className="bg-red-500/15 text-red-400 border-red-500/30"><ShieldAlert className="w-3 h-3 mr-1" />Critical</Badge>;
        }
        return <Badge className="bg-red-500/15 text-red-400 border-red-500/30"><ShieldAlert className="w-3 h-3 mr-1" />Threat</Badge>;
    }

    return <Badge className="bg-green-500/15 text-green-400 border-green-500/30"><ShieldCheck className="w-3 h-3 mr-1" />Clean</Badge>;
}

export default function ReportsPage() {
    const [scans, setScans] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const jobsRes = await scanApi.getJobs(100);
                setScans(jobsRes.jobs || []);
            } catch (err) {
                console.error("Failed to fetch scan history:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchJobs();
    }, []);

    const filteredScans = scans.filter(s => 
        (s.file_name || "").toLowerCase().includes(search.toLowerCase()) || 
        (s.id || "").toLowerCase().includes(search.toLowerCase())
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6 container mx-auto max-w-6xl py-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        <FileText className="w-6 h-6 text-primary" />
                        Scan History & Reports
                    </h1>
                    <p className="text-muted-foreground text-sm">View all previously executed steganography analysis jobs.</p>
                </div>
                
                <div className="w-full sm:w-auto relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <input 
                        type="text"
                        placeholder="Search file name or ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full sm:w-64 bg-black/40 border border-border/50 rounded-md py-2 pl-9 pr-4 text-sm text-white focus:outline-none focus:border-primary/50 transition-colors"
                    />
                </div>
            </div>

            <Card className="glass-card border-border/50">
                <CardContent className="p-0">
                    {filteredScans.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center text-muted-foreground">
                            <FileText className="w-12 h-12 mb-4 opacity-20" />
                            <p className="text-lg">No scans found.</p>
                            {search ? (
                                <p className="text-sm mt-1">Try adjusting your search filters.</p>
                            ) : (
                                <Link to="/scan" className="text-primary hover:underline mt-4">Run a new scan</Link>
                            )}
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="border-border/30 hover:bg-transparent">
                                    <TableHead className="text-muted-foreground">File Name</TableHead>
                                    <TableHead className="text-muted-foreground">Type</TableHead>
                                    <TableHead className="text-muted-foreground">Size</TableHead>
                                    <TableHead className="text-muted-foreground">Verdict</TableHead>
                                    <TableHead className="text-muted-foreground">Confidence</TableHead>
                                    <TableHead className="text-muted-foreground text-right">Date</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredScans.map((scan) => (
                                    <TableRow 
                                        key={scan.id} 
                                        className="border-border/20 hover:bg-white/5 cursor-pointer transition-colors"
                                        onClick={() => navigate(`/scan/results/${scan.id}`)}
                                    >
                                        <TableCell className="font-medium text-white max-w-[220px] truncate" title={scan.file_name}>
                                            {scan.file_name}
                                        </TableCell>
                                        <TableCell className="text-xs text-muted-foreground">{scan.job_type || "image"}</TableCell>
                                        <TableCell className="text-xs text-muted-foreground">{(scan.file_size_bytes / 1024).toFixed(1)} KB</TableCell>
                                        <TableCell><ThreatBadge scan={scan} /></TableCell>
                                        <TableCell className="text-xs font-mono">
                                            {scan.confidence !== null && scan.confidence !== undefined 
                                                ? <span className={scan.is_stego ? "text-red-400" : "text-green-400"}>{(scan.confidence * 100).toFixed(1)}%</span>
                                                : <span className="text-muted-foreground">—</span>
                                            }
                                        </TableCell>
                                        <TableCell className="text-right text-xs text-muted-foreground">
                                            {new Date(scan.created_at).toLocaleString()}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
