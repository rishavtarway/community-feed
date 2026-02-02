/**
 * TanStack Query hook for fetching the post feed.
 */

import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { fetchPosts, fetchPost } from '../api';
import type { Post, PaginatedResponse } from '../types';

/**
 * Hook to fetch paginated post feed.
 * Uses infinite query for potential infinite scroll.
 */
export function useFeed() {
    return useInfiniteQuery<PaginatedResponse<Post>>({
        queryKey: ['posts'],
        queryFn: ({ pageParam = 1 }) => fetchPosts(pageParam as number),
        getNextPageParam: (lastPage, allPages) => {
            if (lastPage.next) {
                return allPages.length + 1;
            }
            return undefined;
        },
        initialPageParam: 1,
    });
}

/**
 * Hook to fetch a single post with nested comments.
 */
export function usePost(id: number) {
    return useQuery<Post>({
        queryKey: ['post', id],
        queryFn: () => fetchPost(id),
        enabled: !!id,
    });
}
