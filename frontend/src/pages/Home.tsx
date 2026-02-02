/**
 * Home page - Main feed displaying posts.
 */

import { useFeed } from '../hooks';
import { PostCard } from '../components/PostCard';
import { Loader2 } from 'lucide-react';

export function Home() {
    const {
        data,
        isLoading,
        error,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage,
    } = useFeed();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-400">Failed to load feed</p>
                <p className="text-gray-500 text-sm mt-1">Please try again later</p>
            </div>
        );
    }

    const posts = data?.pages.flatMap((page) => page.results) ?? [];

    if (posts.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-400">No posts yet</p>
                <p className="text-gray-500 text-sm mt-1">Be the first to post!</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h1 className="text-2xl font-bold text-white mb-6">Community Feed</h1>

            {posts.map((post) => (
                <PostCard key={post.id} post={post} />
            ))}

            {hasNextPage && (
                <div className="flex justify-center py-4">
                    <button
                        onClick={() => fetchNextPage()}
                        disabled={isFetchingNextPage}
                        className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                        {isFetchingNextPage ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Loading...
                            </>
                        ) : (
                            'Load More'
                        )}
                    </button>
                </div>
            )}
        </div>
    );
}
