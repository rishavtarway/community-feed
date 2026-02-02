/**
 * TanStack Query hook for fetching the leaderboard.
 */

import { useQuery } from '@tanstack/react-query';
import { fetchLeaderboard } from '../api';
import type { LeaderboardEntry } from '../types';

/**
 * Hook to fetch the 24h leaderboard.
 * Refetches every 60 seconds for near real-time updates.
 */
export function useLeaderboard() {
    return useQuery<LeaderboardEntry[]>({
        queryKey: ['leaderboard'],
        queryFn: fetchLeaderboard,
        refetchInterval: 60000, // Refetch every 60 seconds
        staleTime: 30000, // Consider data stale after 30 seconds
    });
}
