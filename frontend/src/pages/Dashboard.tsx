import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const metrics = [
  { title: "Total Scans", value: "12,847", trend: "+12.5%", up: true, icon: ScanSearch },
  { title: "Threats Detected", value: "342", trend: "+3.2%", up: true, icon: ShieldAlert },
  { title: "Neutralized", value: "318", trend: "+8.1%", up: true, icon: ShieldCheck },
  { title: "System Health", value: "99.8%", trend: "-0.1%", up: false, icon: Activity },
];

const recentScans = [
  { id: "SCN-7F3A", file: "product_banner.png", type: "Image", status: "Infected", date: "2 min ago" },
  { id: "SCN-8B2C", file: "model_v3.h5", type: "DNN", status: "Clean", date: "15 min ago" },
  { id: "SCN-9D4E", file: "avatar_upload.jpg", type: "Image", status: "Clean", date: "1 hr ago" },
  { id: "SCN-1A5F", file: "checkpoint_epoch50.pt", type: "DNN", status: "Pending", date: "2 hr ago" },
  { id: "SCN-3C7G", file: "header_bg.png", type: "Image", status: "Infected", date: "3 hr ago" },
];

const threatData = [
  { name: "LSB Payload", value: 45 },
  { name: "DCT Embed", value: 25 },
  { name: "DNN Weight", value: 20 },
  { name: "Adaptive", value: 10 },
];

const CHART_COLORS = [
  "hsl(187, 92%, 55%)",
  "hsl(152, 69%, 45%)",
  "hsl(0, 72%, 51%)",
  "hsl(38, 92%, 50%)",
];

function StatusBadge({ status }: { status: string }) {
  if (status === "Clean") return <Badge className="bg-safe/15 text-safe border-safe/30 hover:bg-safe/20">Clean</Badge>;
  if (status === "Infected") return <Badge className="bg-threat/15 text-threat border-threat/30 hover:bg-threat/20">Infected</Badge>;
  return <Badge className="bg-warning/15 text-warning border-warning/30 hover:bg-warning/20">Pending</Badge>;
}

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground text-sm">System overview and recent scanning activity.</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <Card key={m.title} className="glass-card border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">{m.title}</CardTitle>
              <m.icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{m.value}</div>
              <div className={`flex items-center gap-1 text-xs mt-1 ${m.up ? "text-safe" : "text-threat"}`}>
                {m.up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                {m.trend} from last month
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2 glass-card border-border/50">
          <CardHeader>
            <CardTitle className="text-base">Recent Scans</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="border-border/30 hover:bg-transparent">
                  <TableHead className="text-muted-foreground">ID</TableHead>
                  <TableHead className="text-muted-foreground">File</TableHead>
                  <TableHead className="text-muted-foreground">Type</TableHead>
                  <TableHead className="text-muted-foreground">Status</TableHead>
                  <TableHead className="text-muted-foreground text-right">Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentScans.map((scan) => (
                  <TableRow key={scan.id} className="border-border/20 hover:bg-secondary/30">
                    <TableCell className="font-mono text-xs text-primary">{scan.id}</TableCell>
                    <TableCell className="font-mono text-xs">{scan.file}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">{scan.type}</Badge>
                    </TableCell>
                    <TableCell><StatusBadge status={scan.status} /></TableCell>
                    <TableCell className="text-right text-xs text-muted-foreground">{scan.date}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Threat Distribution */}
        <Card className="glass-card border-border/50">
          <CardHeader>
            <CardTitle className="text-base">Threat Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[180px]">
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
                    {threatData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(222, 47%, 8%)",
                      border: "1px solid hsl(222, 30%, 16%)",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {threatData.map((d, i) => (
                <div key={d.name} className="flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[i] }} />
                  <span className="text-muted-foreground">{d.name}</span>
                  <span className="ml-auto font-medium">{d.value}%</span>
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
                <h3 className="font-semibold">Image Scanner</h3>
                <p className="text-sm text-muted-foreground">Upload and analyze images for hidden payloads</p>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
            </CardContent>
          </Link>
        </Card>
        <Card className="glass-card-hover border-border/50 cursor-pointer">
          <Link to="/dnn">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <Brain className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold">DNN Analyzer</h3>
                <p className="text-sm text-muted-foreground">Scan neural network models for weight-based steganography</p>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
            </CardContent>
          </Link>
        </Card>
      </div>
    </div>
  );
}
