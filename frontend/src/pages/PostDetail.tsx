/**
 * PostDetail page - Single post view with threaded comments.
 */

import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, MessageCircle } from 'lucide-react';
import { usePost } from '../hooks';
import { PostCard } from '../components/PostCard';
import { CommentNode } from '../components/CommentNode';

export function PostDetail() {
    const { id } = useParams<{ id: string }>();
    const postId = parseInt(id ?? '0', 10);
    const { data: post, isLoading, error } = usePost(postId);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            </div>
        );
    }

    if (error || !post) {
        return (
            <div className="text-center py-12">
                <p className="text-red-400">Failed to load post</p>
                <Link
                    to="/"
                    className="text-purple-400 hover:text-purple-300 mt-2 inline-block"
                >
                    ← Back to feed
                </Link>
            </div>
        );
    }

    const rootComments = post.comments?.filter((c) => c.parent_id === null) ?? [];

    return (
        <div className="space-y-6">
            {/* Back Button */}
            <Link
                to="/"
                className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to feed</span>
            </Link>

            {/* Post */}
            <PostCard post={post} isDetail />

            {/* Comments Section */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                <div className="p-4 border-b border-gray-700 flex items-center gap-2">
                    <MessageCircle className="w-5 h-5 text-gray-400" />
                    <h2 className="font-semibold text-white">
                        Comments ({post.comments?.length ?? 0})
                    </h2>
                </div>

                {rootComments.length === 0 ? (
                    <div className="p-8 text-center">
                        <p className="text-gray-400">No comments yet</p>
                        <p className="text-gray-500 text-sm mt-1">Be the first to comment!</p>
                    </div>
                ) : (
                    <div className="p-4 space-y-2">
                        {rootComments.map((comment) => (
                            <CommentNode key={comment.id} comment={comment} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
