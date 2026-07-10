from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DSA_KNOWLEDGE_BASE = [
    {
        "topic": "Arrays",
        "content": """Arrays are linear data structures storing elements at contiguous memory locations.
Key operations: access O(1), search O(n), insertion O(n), deletion O(n).
Use arrays when: you need fast access by index, size is fixed.
Common problems: two sum, maximum subarray (Kadane's algorithm), rotate array.
Python: list. Java: int[], ArrayList."""
    },
    {
        "topic": "Binary Search",
        "content": """Binary Search finds an element in a sorted array by repeatedly dividing search space in half.
Time complexity: O(log n). Space: O(1) iterative, O(log n) recursive.
Key condition: array MUST be sorted.
Template: left=0, right=n-1, mid=(left+right)//2
If arr[mid] == target: found. If arr[mid] < target: left=mid+1. Else: right=mid-1.
Common problems: find element, first/last position, search rotated array."""
    },
    {
        "topic": "Linked Lists",
        "content": """Linked List is a linear structure where each node points to the next.
Types: Singly, Doubly, Circular.
Key operations: access O(n), insertion O(1), deletion O(1).
Use when: frequent insertions/deletions, size unknown.
Common problems: reverse linked list, detect cycle (Floyd's algorithm), find middle (slow/fast pointer).
Java: LinkedList. Python: custom Node class."""
    },
    {
        "topic": "Stacks",
        "content": """Stack is LIFO (Last In First Out) data structure.
Key operations: push O(1), pop O(1), peek O(1).
Use when: undo/redo, function call stack, expression evaluation.
Common problems: valid parentheses, next greater element, min stack.
Java: Stack, Deque. Python: list with append/pop."""
    },
    {
        "topic": "Queues",
        "content": """Queue is FIFO (First In First Out) data structure.
Key operations: enqueue O(1), dequeue O(1).
Types: Simple, Circular, Priority Queue, Deque.
Use when: BFS, scheduling, order processing.
Common problems: implement queue using stacks, sliding window maximum.
Java: Queue, LinkedList. Python: collections.deque."""
    },
    {
        "topic": "Trees",
        "content": """Tree is hierarchical data structure with root, parent, child nodes.
Binary Tree: each node has at most 2 children.
BST: left < root < right. Search/insert/delete O(h) where h=height.
Traversals: inorder (left-root-right), preorder (root-left-right), postorder (left-right-root).
Common problems: max depth, validate BST, lowest common ancestor, level order traversal.
Balanced BST height: O(log n). Unbalanced: O(n)."""
    },
    {
        "topic": "Graphs",
        "content": """Graph is collection of vertices and edges.
Types: directed/undirected, weighted/unweighted, cyclic/acyclic.
Representations: adjacency matrix O(V²) space, adjacency list O(V+E) space.
Traversals: BFS (queue, shortest path unweighted), DFS (stack/recursion, cycle detection).
Common problems: number of islands, course schedule, shortest path (Dijkstra), clone graph.
Time complexity: BFS/DFS O(V+E)."""
    },
    {
        "topic": "Dynamic Programming",
        "content": """Dynamic Programming solves problems by breaking into overlapping subproblems.
Two approaches: top-down (memoization), bottom-up (tabulation).
Key insight: optimal substructure + overlapping subproblems.
Steps: define state, find recurrence relation, base cases, fill table.
Common problems: fibonacci, knapsack, longest common subsequence, coin change, climbing stairs.
Time: usually O(n²) or O(n). Space: O(n) or O(n²)."""
    },
    {
        "topic": "Sorting",
        "content": """Common sorting algorithms:
Bubble Sort: O(n²) time, O(1) space. Simple but slow.
Merge Sort: O(n log n) time, O(n) space. Stable, divide and conquer.
Quick Sort: O(n log n) average, O(n²) worst. In-place, fastest in practice.
Heap Sort: O(n log n) time, O(1) space.
Java: Arrays.sort() uses TimSort O(n log n). Python: sorted() uses TimSort.
When to use: small data=insertion sort, general=quicksort, stability needed=mergesort."""
    },
    {
        "topic": "Recursion",
        "content": """Recursion is when a function calls itself to solve smaller subproblems.
Every recursive function needs: base case (stop condition) + recursive case.
Call stack stores each recursive call — too deep causes StackOverflow.
Time: depends on number of calls. Space: O(depth) for call stack.
Common problems: factorial, fibonacci, tower of hanoi, tree traversals, permutations.
Convert to iteration when: deep recursion, performance critical."""
    }
]

vectorizer = TfidfVectorizer()
doc_texts = [f"{d['topic']} {d['content']}" for d in DSA_KNOWLEDGE_BASE]
tfidf_matrix = vectorizer.fit_transform(doc_texts)

def search_dsa_knowledge(query: str, top_k: int = 2) -> list:
    """Search knowledge base and return most relevant topics"""
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(similarities)[::-1][:top_k]
    results = []
    for idx in top_indices:
        if similarities[idx] > 0.0:
            results.append({
                "topic": DSA_KNOWLEDGE_BASE[idx]["topic"],
                "content": DSA_KNOWLEDGE_BASE[idx]["content"],
                "similarity_score": round(float(similarities[idx]), 3)
            })
    return results

def get_dsa_context(query: str) -> str:
    """Get formatted context string for AI prompt"""
    results = search_dsa_knowledge(query)
    if not results:
        return "No relevant DSA content found in knowledge base."
    lines = ["📚 Relevant DSA knowledge found:"]
    for r in results:
        lines.append(f"\n--- {r['topic']} (relevance: {r['similarity_score']}) ---")
        lines.append(r['content'])
    return "\n".join(lines)