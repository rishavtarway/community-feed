/**
 * API functions for the Community Feed.
 */

import apiClient from './client';
import type { Post, LeaderboardEntry, VoteRequest, VoteResponse, PaginatedResponse } from '../types';

/**
 * Fetch paginated list of posts.
 */
export async function fetchPosts(page: number = 1): Promise<PaginatedResponse<Post>> {
    const response = await apiClient.get<PaginatedResponse<Post>>('/posts/', {
        params: { page },
    });
    return response.data;
}

/**
 * Fetch a single post with nested comments.
 */
export async function fetchPost(id: number): Promise<Post> {
    const response = await apiClient.get<Post>(`/posts/${id}/`);
    return response.data;
}

/**
 * Fetch the 24h leaderboard (top 5 users).
 */
export async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
    const response = await apiClient.get<LeaderboardEntry[]>('/leaderboard/');
    return response.data;
}

/**
 * Toggle vote on a post or comment.
 */
export async function toggleVote(data: VoteRequest): Promise<VoteResponse> {
    const response = await apiClient.post<VoteResponse>('/vote/', data);
    return response.data;
}
