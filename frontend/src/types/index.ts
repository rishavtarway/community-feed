/**
 * TypeScript interfaces for the Community Feed API.
 */

export interface User {
    id: number;
    username: string;
}

export interface Comment {
    id: number;
    author: User;
    content: string;
    created_at: string;
    parent_id: number | null;
    replies: Comment[];
    like_count: number;
}

export interface Post {
    id: number;
    author: User;
    content: string;
    created_at: string;
    like_count: number;
    comment_count?: number;
    comments?: Comment[];
    updated_at?: string;
}

export interface LeaderboardEntry {
    rank: number;
    username: string;
    score: number;
}

export interface VoteRequest {
    model: 'post' | 'comment';
    id: number;
}

export interface VoteResponse {
    status: 'created' | 'removed' | 'exists';
    message: string;
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}
