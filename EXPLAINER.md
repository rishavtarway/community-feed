# Community Feed - Technical Explainer

## 1. The Tree (Solving N+1)

We avoided the N+1 problem by avoiding recursive database queries entirely.

* **Strategy:** We fetch the Post and *all* associated comments in exactly **two** queries using `prefetch_related`.
* **Serialization:** We load the flat list of comments into memory (O(n)) and convert them into a hash map (Dictionary), keyed by ID. We then perform a single pass to attach children to their parents. This reduces the complexity from O(N Queries) to O(2 Queries + N CPU cycles).

## 2. The Math (Leaderboard)

To calculate the rolling 24h Karma without storing it:

```sql
SELECT
    content_author_id,
    SUM(
        CASE
            WHEN content_type_model = 'post' THEN 5
            WHEN content_type_model = 'comment' THEN 1
            ELSE 0
        END
    ) as score
FROM votes
-- Join logic handles traversing from Vote -> Content -> Author
WHERE created_at >= NOW() - INTERVAL '24 HOURS'
GROUP BY content_author_id
ORDER BY score DESC
LIMIT 5;
```

## 3. Concurrency Handling

* **The Problem:** Multiple users clicking "Like" simultaneously could create duplicate votes.
* **The Solution:** Database-level `UniqueConstraint` on `(user, content_type, object_id)` combined with `transaction.atomic()` and `IntegrityError` catching ensures idempotent vote toggling.