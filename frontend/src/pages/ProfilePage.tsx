import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User as UserIcon, Mail, ShieldAlert } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

const ProfilePage = () => {
    const { user, logout } = useAuthStore();
    const { toast } = useToast();

    const handleLogout = async () => {
        try {
            await logout();
            toast({
                title: "Logged out",
                description: "You have been successfully logged out.",
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to log out.",
                variant: "destructive",
            });
        }
    };

    if (!user) return null;

    return (
        <div className="container max-w-4xl py-8 animate-fade-in">
            <div className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight text-foreground">Account Profile</h1>
                <p className="text-muted-foreground mt-2">
                    Manage your StegoHunter account settings and preferences.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-[1fr_250px] lg:grid-cols-[1fr_300px]">
                <div className="space-y-6">
                    <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                        <CardHeader>
                            <CardTitle>Profile Details</CardTitle>
                            <CardDescription>
                                Information associated with your analyst account.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="flex items-center gap-6 mb-6">
                                <Avatar className="h-20 w-20 border-2 border-primary/20">
                                    <AvatarFallback className="bg-primary/10 text-primary text-xl">
                                        {user.username.charAt(0).toUpperCase()}
                                    </AvatarFallback>
                                </Avatar>
                                <div>
                                    <h3 className="text-xl font-medium">{user.username}</h3>
                                    <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                                        <ShieldAlert className="h-4 w-4 text-primary" />
                                        <span className="capitalize">{user.role}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="username">Username</Label>
                                    <div className="relative">
                                        <UserIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="username"
                                            defaultValue={user.username}
                                            className="pl-9"
                                            readOnly
                                        />
                                    </div>
                                </div>

                                <div className="grid gap-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="email"
                                            defaultValue={user.email}
                                            className="pl-9"
                                            readOnly
                                        />
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="border-t border-border/50 bg-muted/20 px-6 py-4">
                            <p className="text-xs text-muted-foreground truncate">
                                Account ID: {user.id}
                            </p>
                        </CardFooter>
                    </Card>
                </div>

                <div className="space-y-6">
                    <Card className="border-destructive/20 bg-destructive/5">
                        <CardHeader>
                            <CardTitle className="text-destructive">Danger Zone</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground mb-4">
                                End your current session line securely.
                            </p>
                            <Button
                                variant="destructive"
                                className="w-full"
                                onClick={handleLogout}
                            >
                                Sign Out
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
