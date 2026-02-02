/**
 * LikeButton - Reusable like button with optimistic UI.
 */

import { Heart } from 'lucide-react';
import { useVote } from '../hooks';

interface LikeButtonProps {
    modelType: 'post' | 'comment';
    id: number;
    likeCount: number;
}

export function LikeButton({ modelType, id, likeCount }: LikeButtonProps) {
    const { mutate: vote, isPending } = useVote();

    const handleClick = () => {
        if (isPending) return;
        vote({ model: modelType, id });
    };

    return (
        <button
            onClick={handleClick}
            disabled={isPending}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm transition-all ${isPending
                    ? 'opacity-50 cursor-not-allowed'
                    : 'hover:bg-red-500/20 hover:text-red-400'
                } text-gray-400`}
        >
            <Heart
                className={`w-4 h-4 ${isPending ? 'animate-pulse' : ''}`}
                fill={isPending ? 'currentColor' : 'none'}
            />
            <span>{likeCount}</span>
        </button>
    );
}
