/**
 * CommentNode - Recursive component for threaded comments.
 * 
 * Renders a comment and recursively renders its replies with
 * increasing left margin to show nesting depth.
 */

import { Clock } from 'lucide-react';
import { LikeButton } from './LikeButton';
import type { Comment } from '../types';

interface CommentNodeProps {
    comment: Comment;
    depth?: number;
}

export function CommentNode({ comment, depth = 0 }: CommentNodeProps) {
    const maxDepth = 5; // Limit nesting to prevent extreme indentation
    const timeAgo = formatTimeAgo(comment.created_at);

    return (
        <div className={depth > 0 ? 'ml-4 pl-4 border-l-2 border-gray-700' : ''}>
            <div className="py-3">
                {/* Comment Header */}
                <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white text-xs font-bold">
                        {comment.author.username.charAt(0).toUpperCase()}
                    </div>
                    <span className="font-medium text-white text-sm">
                        {comment.author.username}
                    </span>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>{timeAgo}</span>
                    </div>
                </div>

                {/* Comment Content */}
                <p className="text-gray-300 text-sm whitespace-pre-wrap ml-9">
                    {comment.content}
                </p>

                {/* Comment Actions */}
                <div className="ml-9 mt-2">
                    <LikeButton
                        modelType="comment"
                        id={comment.id}
                        likeCount={comment.like_count}
                    />
                </div>
            </div>

            {/* Recursive Replies */}
            {comment.replies && comment.replies.length > 0 && (
                <div className="mt-1">
                    {comment.replies.map((reply) => (
                        <CommentNode
                            key={reply.id}
                            comment={reply}
                            depth={Math.min(depth + 1, maxDepth)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

/**
 * Format a timestamp to relative time.
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
