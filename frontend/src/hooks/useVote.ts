/**
 * TanStack Query hook for voting with optimistic updates.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toggleVote } from '../api';

/**
 * Hook for voting on posts/comments.
 * Provides optimistic UI updates that revert on API failure.
 */
export function useVote() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: toggleVote,
        onSuccess: () => {
            // Invalidate queries to refetch updated data
            queryClient.invalidateQueries({ queryKey: ['posts'] });
            queryClient.invalidateQueries({ queryKey: ['post'] });
            queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
        },
    });
}
