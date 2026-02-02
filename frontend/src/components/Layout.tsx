/**
 * Layout - Responsive grid with navbar and leaderboard sidebar.
 */

import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Rocket } from 'lucide-react';
import { LeaderboardWidget } from './LeaderboardWidget';

interface LayoutProps {
    children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
    return (
        <div className="min-h-screen bg-gray-900">
            {/* Navbar */}
            <header className="sticky top-0 z-50 bg-gray-900/95 backdrop-blur border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2 group">
                        <Rocket className="w-7 h-7 text-purple-500 group-hover:text-purple-400 transition-colors" />
                        <span className="text-xl font-bold text-white">
                            Playto<span className="text-purple-500">Feed</span>
                        </span>
                    </Link>
                </div>
            </header>

            {/* Main Content Grid */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Content Area */}
                    <main className="lg:col-span-2">{children}</main>

                    {/* Sidebar - Desktop only */}
                    <aside className="hidden lg:block">
                        <div className="sticky top-20">
                            <LeaderboardWidget />
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
}
