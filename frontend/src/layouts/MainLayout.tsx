import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
    ShieldAlert,
    LayoutDashboard,
    Scan,
    Settings,
    FileText,
    Activity,
    LogOut
} from 'lucide-react';

const MainLayout = () => {
    const location = useLocation();

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'New Scan', href: '/scan', icon: Scan },
        { name: 'Neutralize Engine', href: '/neutralize', icon: ShieldAlert },
        { name: 'DNN Analysis', href: '/dnn-analysis', icon: Activity },
        { name: 'Reports', href: '/reports', icon: FileText },
        { name: 'Admin', href: '/admin', icon: Settings },
    ];

    return (
        <div className="flex h-screen bg-neutral-900 text-white font-sans">
            {/* Sidebar */}
            <div className="w-64 bg-neutral-950 border-r border-neutral-800 flex flex-col">
                <div className="h-16 flex items-center px-6 border-b border-neutral-800">
                    <ShieldAlert className="w-8 h-8 text-emerald-500 mr-3" />
                    <span className="text-xl font-bold tracking-wider">STEGO<span className="text-emerald-500">HUNTER</span></span>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
                    {navigation.map((item) => {
                        const isActive = location.pathname.startsWith(item.href);
                        return (
                            <Link
                                key={item.name}
                                to={item.href}
                                className={`flex items-center px-4 py-3 rounded-lg transition-colors ${isActive
                                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                        : 'text-neutral-400 hover:bg-neutral-800 hover:text-white'
                                    }`}
                            >
                                <item.icon className="w-5 h-5 mr-3" />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-neutral-800">
                    <button className="flex items-center w-full px-4 py-2 text-neutral-400 hover:text-rose-400 transition-colors">
                        <LogOut className="w-5 h-5 mr-3" />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-16 bg-neutral-950 border-b border-neutral-800 flex items-center justify-between px-8">
                    <h1 className="text-xl font-semibold capitalize">
                        {location.pathname.split('/')[1] || 'Dashboard'}
                    </h1>
                    <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-emerald-400 font-bold">
                            N
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-auto p-8 bg-neutral-900">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
