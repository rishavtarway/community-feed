/**
 * PostCard - Displays a post with author, content, and like button.
 */

import { Link } from 'react-router-dom';
import { MessageCircle, Clock } from 'lucide-react';
import { LikeButton } from './LikeButton';
import type { Post } from '../types';

interface PostCardProps {
    post: Post;
    isDetail?: boolean;
}

export function PostCard({ post, isDetail = false }: PostCardProps) {
    const timeAgo = formatTimeAgo(post.created_at);

    return (
        <article className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors">
            <div className="p-4">
                {/* Header */}
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold">
                        {post.author.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <p className="font-medium text-white">{post.author.username}</p>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                            <Clock className="w-3 h-3" />
                            <span>{timeAgo}</span>
                        </div>
                    </div>
                </div>

                {/* Content */}
                {isDetail ? (
                    <p className="text-gray-200 whitespace-pre-wrap">{post.content}</p>
                ) : (
                    <Link to={`/post/${post.id}`} className="block group">
                        <p className="text-gray-200 group-hover:text-white transition-colors line-clamp-3">
                            {post.content}
                        </p>
                    </Link>
                )}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 bg-gray-800/50 border-t border-gray-700 flex items-center gap-4">
                <LikeButton modelType="post" id={post.id} likeCount={post.like_count} />

                {!isDetail && post.comment_count !== undefined && (
                    <Link
                        to={`/post/${post.id}`}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm text-gray-400 hover:bg-blue-500/20 hover:text-blue-400 transition-all"
                    >
                        <MessageCircle className="w-4 h-4" />
                        <span>{post.comment_count}</span>
                    </Link>
                )}
            </div>
        </article>
    );
}

/**
 * Format a timestamp to relative time (e.g., "2 hours ago").
 */
function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}
