/**
 * LeaderboardWidget - Displays top 5 users by 24h karma.
 */

import { Trophy, TrendingUp } from 'lucide-react';
import { useLeaderboard } from '../hooks';

export function LeaderboardWidget() {
    const { data: leaderboard, isLoading, error } = useLeaderboard();

    return (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
                <Trophy className="w-5 h-5 text-yellow-500" />
                <h2 className="text-lg font-semibold text-white">Top Contributors</h2>
            </div>
            <p className="text-xs text-gray-500 mb-3">Last 24 hours</p>

            {isLoading && (
                <div className="space-y-2">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="h-8 bg-gray-700 rounded animate-pulse" />
                    ))}
                </div>
            )}

            {error && (
                <p className="text-red-400 text-sm">Failed to load leaderboard</p>
            )}

            {leaderboard && leaderboard.length === 0 && (
                <p className="text-gray-400 text-sm">No activity yet</p>
            )}

            {leaderboard && leaderboard.length > 0 && (
                <ul className="space-y-2">
                    {leaderboard.map((entry) => (
                        <li
                            key={entry.rank}
                            className="flex items-center justify-between py-2 px-3 rounded bg-gray-700/50 hover:bg-gray-700 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <span
                                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${entry.rank === 1
                                            ? 'bg-yellow-500 text-black'
                                            : entry.rank === 2
                                                ? 'bg-gray-400 text-black'
                                                : entry.rank === 3
                                                    ? 'bg-amber-600 text-white'
                                                    : 'bg-gray-600 text-gray-300'
                                        }`}
                                >
                                    {entry.rank}
                                </span>
                                <span className="text-white font-medium">{entry.username}</span>
                            </div>
                            <div className="flex items-center gap-1 text-green-400">
                                <TrendingUp className="w-4 h-4" />
                                <span className="font-semibold">{entry.score}</span>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
