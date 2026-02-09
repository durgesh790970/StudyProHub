"""
Django management command to seed sample questions for the interview test system.
Creates 20 questions for each (company, difficulty) combination.
Companies: Google, OpenAI, Uber, Microsoft
Difficulties: Easy, Medium, Hard
Total: 240 questions (4 companies × 3 difficulties × 20 questions)
"""

from django.core.management.base import BaseCommand
from accounts.models import Question

QUESTIONS_DATA = {
    ('google', 'easy'): [
        {
            'question_text': 'Which data structure works on FIFO principle?',
            'option_a': 'Stack',
            'option_b': 'Queue',
            'option_c': 'Tree',
            'option_d': 'Graph',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Time complexity of binary search?',
            'option_a': 'O(n²)',
            'option_b': 'O(n)',
            'option_c': 'O(log n)',
            'option_d': 'O(1)',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Which keyword is used to create a class in Java?',
            'option_a': 'struct',
            'option_b': 'create',
            'option_c': 'class',
            'option_d': 'new',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Full form of CPU?',
            'option_a': 'Control Program Utility',
            'option_b': 'Central Processing Unit',
            'option_c': 'Compute Power Unit',
            'option_d': 'Central Program Utility',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which of these is not an OOP concept?',
            'option_a': 'Encapsulation',
            'option_b': 'Polymorphism',
            'option_c': 'Routing',
            'option_d': 'Inheritance',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'RAM stands for?',
            'option_a': 'Random Access Memory',
            'option_b': 'Readable Access Machine',
            'option_c': 'Rapid Access Memory',
            'option_d': 'Random Arithmetic Mode',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'Which symbol is used for comments in Python?',
            'option_a': '//',
            'option_b': '<!-- -->',
            'option_c': '#',
            'option_d': '/* */',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'What is the extension of a C++ file?',
            'option_a': '.py',
            'option_b': '.cpp',
            'option_c': '.java',
            'option_d': '.js',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which sorting technique is fastest on average?',
            'option_a': 'Bubble',
            'option_b': 'Insertion',
            'option_c': 'Quick sort',
            'option_d': 'Selection',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'HTML stands for?',
            'option_a': 'Hyper Text Make Language',
            'option_b': 'Hyper Test Markup Language',
            'option_c': 'Hyper Text Markup Language',
            'option_d': 'Higher Text Management Language',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Which is example of OS?',
            'option_a': 'Google',
            'option_b': 'Windows',
            'option_c': 'Chrome',
            'option_d': 'NodeJS',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which is a NoSQL DB?',
            'option_a': 'MySQL',
            'option_b': 'MongoDB',
            'option_c': 'Oracle',
            'option_d': 'SQL Server',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which command shows git status?',
            'option_a': 'git list',
            'option_b': 'git show',
            'option_c': 'git status',
            'option_d': 'git push',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Which is smallest unit of memory?',
            'option_a': 'Byte',
            'option_b': 'Bit',
            'option_c': 'KB',
            'option_d': 'MB',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which protocol is used for sending emails?',
            'option_a': 'SMTP',
            'option_b': 'HTTP',
            'option_c': 'FTP',
            'option_d': 'SNMP',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'Which layer of OSI handles routing?',
            'option_a': 'Application',
            'option_b': 'Transport',
            'option_c': 'Network',
            'option_d': 'Physical',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Python is a ______ language',
            'option_a': 'compiled',
            'option_b': 'interpreted',
            'option_c': 'binary',
            'option_d': 'static',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which one is frontend framework?',
            'option_a': 'ReactJS',
            'option_b': 'Flask',
            'option_c': 'Django',
            'option_d': 'Laravel',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'IP address length in IPv4?',
            'option_a': '8 bits',
            'option_b': '16 bits',
            'option_c': '32 bits',
            'option_d': '64 bits',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'What does SQL stand for?',
            'option_a': 'Structured Query Language',
            'option_b': 'Simple Query Language',
            'option_c': 'Super Question Language',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': ''
        },
    ],
    ('google', 'medium'): [
        {
            'question_text': 'Which tree traversal prints root, left subtree, then right subtree?',
            'option_a': 'Inorder',
            'option_b': 'Postorder',
            'option_c': 'Preorder',
            'option_d': 'Reverse',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Load factor of Hash Table?',
            'option_a': 'n/m',
            'option_b': 'm/n',
            'option_c': 'n*m',
            'option_d': 'n-1',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'Worst time complexity of Merge Sort?',
            'option_a': 'O(n)',
            'option_b': 'O(n log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(log n)',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'What is deadlock?',
            'option_a': 'multiple requests handling',
            'option_b': 'waiting forever',
            'option_c': 'process terminated',
            'option_d': 'memory full',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Relation between stack and recursion?',
            'option_a': 'Recursion uses heap',
            'option_b': 'recursion uses stack internally',
            'option_c': 'no relation',
            'option_d': 'array inside',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'SQL command to remove data only?',
            'option_a': 'delete',
            'option_b': 'drop',
            'option_c': 'truncate',
            'option_d': 'remove',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'BFS uses which structure?',
            'option_a': 'stack',
            'option_b': 'queue',
            'option_c': 'array',
            'option_d': 'linked list',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'What is race condition?',
            'option_a': 'scheduling',
            'option_b': 'process executes simultaneously causing conflict',
            'option_c': 'priority change',
            'option_d': 'thread locking',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Page replacement algorithm?',
            'option_a': 'FIFO',
            'option_b': 'DDA',
            'option_c': 'DMA',
            'option_d': 'DCA',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'What is mutex?',
            'option_a': 'CPU assignment',
            'option_b': 'lock for synchronization',
            'option_c': 'thread copy',
            'option_d': 'memory swap',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which one is dynamic programming approach?',
            'option_a': 'greedy',
            'option_b': 'divide & conquer',
            'option_c': 'backtracking',
            'option_d': 'overlapping subproblems',
            'correct_answer': 'D',
            'explanation': ''
        },
        {
            'question_text': 'Which ML model is used for classification?',
            'option_a': 'Linear regression',
            'option_b': 'Logistic regression',
            'option_c': 'K-means',
            'option_d': 'PCA',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Cache memory is —',
            'option_a': 'Fastest',
            'option_b': 'Slowest',
            'option_c': 'External',
            'option_d': 'none',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'OS scheduling for time sharing?',
            'option_a': 'SJF',
            'option_b': 'FCFS',
            'option_c': 'Round Robin',
            'option_d': 'Priority',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'What is pointer in C?',
            'option_a': 'stores functions',
            'option_b': 'stores values',
            'option_c': 'stores address',
            'option_d': 'stores string',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Which is lossless join in DBMS?',
            'option_a': 'Normalization',
            'option_b': 'ER Diagram',
            'option_c': 'Decomposition',
            'option_d': 'Triggers',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Gradient descent used for?',
            'option_a': 'minimize error',
            'option_b': 'maximize score',
            'option_c': 'store weights',
            'option_d': 'make layers',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'REST API uses which protocol?',
            'option_a': 'SMTP',
            'option_b': 'HTTP',
            'option_c': 'FTP',
            'option_d': 'SSH',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which is not cloud provider?',
            'option_a': 'AWS',
            'option_b': 'Azure',
            'option_c': 'GCP',
            'option_d': 'Oracle SQL',
            'correct_answer': 'D',
            'explanation': ''
        },
        {
            'question_text': 'Which layer encrypts data?',
            'option_a': 'Presentation',
            'option_b': 'Network',
            'option_c': 'Session',
            'option_d': 'Transport',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'What is the time complexity of finding LCS (Longest Common Subsequence) using dynamic programming?',
            'option_a': 'O(m*n)',
            'option_b': 'O(m+n)',
            'option_c': 'O(m²+n²)',
            'option_d': 'O((m+n)²)',
            'correct_answer': 'A',
            'explanation': 'LCS DP solution has time complexity O(m*n) where m and n are the lengths of two strings.'
        },
        {
            'question_text': 'In a trie data structure, what is the time complexity of insertion?',
            'option_a': 'O(1)',
            'option_b': 'O(m) where m is the length of the string',
            'option_c': 'O(m*n) where n is the number of strings',
            'option_d': 'O(m²)',
            'correct_answer': 'B',
            'explanation': 'Trie insertion is O(m) where m is the length of the string being inserted.'
        },
        {
            'question_text': 'What is the space complexity of a trie with k unique characters and n words?',
            'option_a': 'O(n)',
            'option_b': 'O(k*n)',
            'option_c': 'O(k^n)',
            'option_d': 'O(n²)',
            'correct_answer': 'B',
            'explanation': 'Trie space complexity is O(k*n) in the worst case, where k is alphabet size and n is total characters.'
        },
        {
            'question_text': 'Which algorithm is used to find the shortest path in a weighted directed graph?',
            'option_a': 'BFS',
            'option_b': 'DFS',
            'option_c': 'Dijkstra\'s Algorithm',
            'option_d': 'Both A and B',
            'correct_answer': 'C',
            'explanation': 'Dijkstra\'s algorithm finds the shortest path in weighted graphs with non-negative weights.'
        },
        {
            'question_text': 'What is the time complexity of the Knapsack problem using dynamic programming?',
            'option_a': 'O(n*W) where n is items and W is capacity',
            'option_b': 'O(2^n)',
            'option_c': 'O(n²)',
            'option_d': 'O(n log n)',
            'correct_answer': 'A',
            'explanation': '0/1 Knapsack DP solution has O(n*W) time complexity where W is the knapsack capacity.'
        },
        {
            'question_text': 'Which data structure is best for implementing a priority queue?',
            'option_a': 'Array',
            'option_b': 'Linked List',
            'option_c': 'Heap',
            'option_d': 'Stack',
            'correct_answer': 'C',
            'explanation': 'Heap is the most efficient data structure for priority queue operations.'
        },
        {
            'question_text': 'What is the space complexity of a balanced BST with n nodes?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(n)',
            'option_d': 'O(n²)',
            'correct_answer': 'C',
            'explanation': 'A balanced BST with n nodes requires O(n) space to store all nodes.'
        },
        {
            'question_text': 'Which sorting algorithm is best for nearly sorted data?',
            'option_a': 'Quick Sort',
            'option_b': 'Merge Sort',
            'option_c': 'Insertion Sort',
            'option_d': 'Heap Sort',
            'correct_answer': 'C',
            'explanation': 'Insertion Sort performs best on nearly sorted data with O(n) best-case complexity.'
        },
        {
            'question_text': 'What is the time complexity of finding the median of two sorted arrays?',
            'option_a': 'O(n+m)',
            'option_b': 'O(log(n+m))',
            'option_c': 'O(n*m)',
            'option_d': 'O((n+m)²)',
            'correct_answer': 'B',
            'explanation': 'Using binary search, we can find the median of two sorted arrays in O(log(n+m)) time.'
        },
        {
            'question_text': 'In Union-Find (Disjoint Set Union), what is the time complexity with path compression?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(α(n)) - inverse Ackermann',
            'option_d': 'O(n)',
            'correct_answer': 'C',
            'explanation': 'With path compression, union-find operations have nearly O(1) complexity, precisely O(α(n)).'
        },
        {
            'question_text': 'What is the recurrence relation for merge sort?',
            'option_a': 'T(n) = T(n-1) + O(n)',
            'option_b': 'T(n) = 2*T(n/2) + O(n)',
            'option_c': 'T(n) = T(n/2) + O(1)',
            'option_d': 'T(n) = T(n-2) + O(n)',
            'correct_answer': 'B',
            'explanation': 'Merge sort divides into 2 halves and merges in linear time: T(n) = 2*T(n/2) + O(n).'
        },
        {
            'question_text': 'How many comparisons are needed to find both minimum and maximum in an unsorted array of n elements?',
            'option_a': 'n',
            'option_b': '2n-2',
            'option_c': 'n-1',
            'option_d': 'n+1',
            'correct_answer': 'B',
            'explanation': 'We need 2n-2 comparisons minimum to find both min and max: n-1 for min and n for max (one element done).'
        },
        {
            'question_text': 'What is the time complexity of BFS in a graph with V vertices and E edges?',
            'option_a': 'O(V)',
            'option_b': 'O(E)',
            'option_c': 'O(V+E)',
            'option_d': 'O(V*E)',
            'correct_answer': 'C',
            'explanation': 'BFS visits each vertex once and each edge once, resulting in O(V+E) time complexity.'
        },
        {
            'question_text': 'Which algorithm finds the minimum spanning tree?',
            'option_a': 'Dijkstra\'s Algorithm',
            'option_b': 'Kruskal\'s or Prim\'s Algorithm',
            'option_c': 'Bellman-Ford',
            'option_d': 'Floyd-Warshall',
            'correct_answer': 'B',
            'explanation': 'Kruskal\'s and Prim\'s algorithms are used to find the minimum spanning tree.'
        },
        {
            'question_text': 'What is the space complexity of the edit distance algorithm using DP?',
            'option_a': 'O(m*n)',
            'option_b': 'O(min(m,n))',
            'option_c': 'O(m+n)',
            'option_d': 'O(1)',
            'correct_answer': 'A',
            'explanation': 'Standard edit distance DP requires O(m*n) space for the DP table, but can be optimized to O(min(m,n)).'
        },
        {
            'question_text': 'In segment trees, what is the query time complexity?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(n)',
            'option_d': 'O(n log n)',
            'correct_answer': 'B',
            'explanation': 'Segment tree queries have O(log n) time complexity.'
        },
        {
            'question_text': 'What is the time complexity of constructing a segment tree from an array?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(n)',
            'option_d': 'O(n log n)',
            'correct_answer': 'C',
            'explanation': 'Building a segment tree requires O(n) time as we process each element.'
        },
        {
            'question_text': 'Which of the following is a self-balancing BST?',
            'option_a': 'Red-Black Tree',
            'option_b': 'AVL Tree',
            'option_c': 'B-Tree',
            'option_d': 'All of the above',
            'correct_answer': 'D',
            'explanation': 'All three are self-balancing binary search trees that maintain balance during insertions/deletions.'
        },
    ],
    ('google', 'hard'): [
        {
            'question_text': 'Time complexity of finding median in unsorted array?',
            'option_a': 'O(n log n)',
            'option_b': 'O(n²)',
            'option_c': 'O(n)',
            'option_d': 'O(log n)',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Travelling Salesman Problem solved optimally by?',
            'option_a': 'Greedy',
            'option_b': 'DP',
            'option_c': 'BFS',
            'option_d': 'Binary Search',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Maximum subarray sum algorithm?',
            'option_a': 'Floyd',
            'option_b': 'Kadane',
            'option_c': 'Dijkstra',
            'option_d': 'Bellman Ford',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'CAP theorem says?',
            'option_a': 'Cache API Performance',
            'option_b': 'Consistency, Availability, Partition tolerance',
            'option_c': 'Control Access Protocol',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Optimal binary search tree technique?',
            'option_a': 'greedy',
            'option_b': 'DP',
            'option_c': 'branch & bound',
            'option_d': 'backtracking',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Which model avoids vanishing gradient problem?',
            'option_a': 'CNN',
            'option_b': 'RNN',
            'option_c': 'LSTM',
            'option_d': 'Naive Bayes',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Which indexing technique fastest for search?',
            'option_a': 'BFS',
            'option_b': 'B+ Tree',
            'option_c': 'Heap',
            'option_d': 'Pointer',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'What is sharding in DBMS?',
            'option_a': 'backup',
            'option_b': 'horizontal partitioning',
            'option_c': 'vertical split',
            'option_d': 'encryption',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'Feature scaling method?',
            'option_a': 'PCA',
            'option_b': 'Standardization',
            'option_c': 'Confidence Binning',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'O(n log n) solution for shortest path?',
            'option_a': 'BFS',
            'option_b': 'DFS',
            'option_c': 'Dijkstra with priority queue',
            'option_d': 'DP',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'NP-Hard problem example',
            'option_a': 'Bubble sort',
            'option_b': 'TSP',
            'option_c': 'BFS',
            'option_d': 'SJF',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'What is backpropagation used for?',
            'option_a': 'Update weights',
            'option_b': 'select layers',
            'option_c': 'remove neurons',
            'option_d': 'image preprocessing',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'Conv layer uses?',
            'option_a': 'pooling',
            'option_b': 'matrix multiplication',
            'option_c': 'convolution filters',
            'option_d': 'accuracy',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'In distributed systems, consensus algorithm?',
            'option_a': 'Raft',
            'option_b': 'DFS',
            'option_c': 'DDA',
            'option_d': 'DRS',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'AVL tree maintains?',
            'option_a': 'BFS order',
            'option_b': 'depth difference ≤1',
            'option_c': 'full binary',
            'option_d': 'complete',
            'correct_answer': 'B',
            'explanation': ''
        },
        {
            'question_text': 'LRU stands for?',
            'option_a': 'Least Recently Used',
            'option_b': 'Last Reaction Unit',
            'option_c': 'Low Running Utility',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'Which tracks dependency update in ML?',
            'option_a': 'Git',
            'option_b': 'GitLFS',
            'option_c': 'MLOps',
            'option_d': 'Docker',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'A* algorithm uses?',
            'option_a': 'heuristic + cost',
            'option_b': 'min cost',
            'option_c': 'greedy only',
            'option_d': 'cost only',
            'correct_answer': 'A',
            'explanation': ''
        },
        {
            'question_text': 'Transformer architecture uses?',
            'option_a': 'RNN',
            'option_b': 'CNN',
            'option_c': 'Attention mechanism',
            'option_d': 'Autoencoder',
            'correct_answer': 'C',
            'explanation': ''
        },
        {
            'question_text': 'Blockchain uses which data structure?',
            'option_a': 'array',
            'option_b': 'tree',
            'option_c': 'linked list',
            'option_d': 'hash chain',
            'correct_answer': 'D',
            'explanation': ''
        },
        {
            'question_text': 'What is the optimal time complexity for finding the median in a stream of integers?',
            'option_a': 'O(1) for all operations',
            'option_b': 'O(log n) insertion, O(1) query',
            'option_c': 'O(n) for all operations',
            'option_d': 'O(log n) for both',
            'correct_answer': 'B',
            'explanation': 'Using two heaps (max and min), we get O(log n) insertion and O(1) median query.'
        },
        {
            'question_text': 'Design a data structure for LRU Cache. What are the time complexities?',
            'option_a': 'O(1) for get and put',
            'option_b': 'O(log n) for get and O(1) for put',
            'option_c': 'O(n) for both operations',
            'option_d': 'O(1) for get and O(n) for put',
            'correct_answer': 'A',
            'explanation': 'Using HashMap and Doubly Linked List, both get and put operations are O(1).'
        },
        {
            'question_text': 'What is the time complexity of topological sort using DFS?',
            'option_a': 'O(V)',
            'option_b': 'O(E)',
            'option_c': 'O(V+E)',
            'option_d': 'O(V*E)',
            'correct_answer': 'C',
            'explanation': 'Topological sort using DFS has time complexity O(V+E) where V is vertices and E is edges.'
        },
        {
            'question_text': 'Design a suffix array. What is the space complexity?',
            'option_a': 'O(n)',
            'option_b': 'O(n log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(2^n)',
            'correct_answer': 'A',
            'explanation': 'A suffix array uses O(n) space to store n suffixes with their indices.'
        },
        {
            'question_text': 'What is the optimal solution for the problem: Find the longest increasing subsequence?',
            'option_a': 'O(n²) DP solution',
            'option_b': 'O(n log n) with binary search',
            'option_c': 'O(n) greedy solution',
            'option_d': 'O(2^n) brute force',
            'correct_answer': 'B',
            'explanation': 'The optimal solution uses binary search on DP array achieving O(n log n) time complexity.'
        },
        {
            'question_text': 'In the Convex Hull problem, which algorithm is optimal?',
            'option_a': 'Graham\'s Scan with O(n log n)',
            'option_b': 'Jarvis March with O(n*h)',
            'option_c': 'Brute Force with O(n³)',
            'option_d': 'A is optimal for general case',
            'correct_answer': 'D',
            'explanation': 'Graham\'s Scan is optimal with O(n log n) for most cases, though Jarvis is better when h << n.'
        },
        {
            'question_text': 'What is the space complexity of storing a string suffix tree?',
            'option_a': 'O(n)',
            'option_b': 'O(n log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(n) with suffix array compression',
            'correct_answer': 'A',
            'explanation': 'A suffix tree can be built and stored in O(n) space using algorithms like Ukkonen\'s.'
        },
        {
            'question_text': 'For the problem: given n ropes, join them with minimum cost. What\'s the approach?',
            'option_a': 'Greedy - always join two smallest',
            'option_b': 'DP - try all combinations',
            'option_c': 'Use Min Heap',
            'option_d': 'A and C are equivalent',
            'correct_answer': 'D',
            'explanation': 'The greedy approach using a min heap (priority queue) is optimal for joining ropes.'
        },
        {
            'question_text': 'What is the worst-case space complexity of quicksort?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(n)',
            'option_d': 'O(n²)',
            'correct_answer': 'C',
            'explanation': 'Quicksort worst-case space is O(n) when recursion stack grows to n (skewed pivot).'
        },
        {
            'question_text': 'In the N-Queens problem, what is the time complexity of backtracking solution?',
            'option_a': 'O(n)',
            'option_b': 'O(n!)',
            'option_c': 'O(2^n)',
            'option_d': 'O(n²)',
            'correct_answer': 'B',
            'explanation': 'N-Queens backtracking explores n! permutations in the worst case.'
        },
        {
            'question_text': 'Design a memory allocator. What\'s the best approach?',
            'option_a': 'First Fit',
            'option_b': 'Best Fit',
            'option_c': 'Worst Fit',
            'option_d': 'Depends on usage patterns',
            'correct_answer': 'D',
            'explanation': 'The best allocation strategy depends on the pattern: First Fit is fast, Best Fit minimizes fragmentation.'
        },
        {
            'question_text': 'For very large graphs, which representation is most memory efficient?',
            'option_a': 'Adjacency Matrix',
            'option_b': 'Adjacency List',
            'option_c': 'Incidence Matrix',
            'option_d': 'Edge List',
            'correct_answer': 'B',
            'explanation': 'Adjacency List is O(V+E) space, much better than Matrix\'s O(V²) for sparse graphs.'
        },
        {
            'question_text': 'What is the optimal solution for: Maximum subarray with at most k elements removed?',
            'option_a': 'O(n) with DP',
            'option_b': 'O(n*k) with DP',
            'option_c': 'O(n²) with brute force',
            'option_d': 'Cannot be solved optimally',
            'correct_answer': 'B',
            'explanation': 'This requires O(n*k) DP solution where dp[i][j] = max sum using first i elements, removing at most j.'
        },
        {
            'question_text': 'In Fenwick Tree (Binary Indexed Tree), what is query range time complexity?',
            'option_a': 'O(1)',
            'option_b': 'O(log n)',
            'option_c': 'O(√n)',
            'option_d': 'O(n)',
            'correct_answer': 'B',
            'explanation': 'Fenwick Tree provides O(log n) time for both point updates and range queries.'
        },
        {
            'question_text': 'What is the space-time tradeoff in the Meet-in-the-Middle approach?',
            'option_a': 'O(2^n) time, O(1) space',
            'option_b': 'O(2^(n/2)) time, O(2^(n/2)) space',
            'option_c': 'O(n) time, O(n²) space',
            'option_d': 'O(n²) time, O(n) space',
            'correct_answer': 'B',
            'explanation': 'Meet-in-the-Middle reduces exponential complexity by splitting and using O(2^(n/2)) space.'
        },
        {
            'question_text': 'For the Traveling Salesman Problem, what is the best known complexity?',
            'option_a': 'O(n²)',
            'option_b': 'O(n² * 2^n) using DP',
            'option_c': 'Polynomial time (not proven)',
            'option_d': 'Only exponential solutions exist',
            'correct_answer': 'B',
            'explanation': 'TSP can be solved in O(n² * 2^n) using dynamic programming (Held-Karp algorithm).'
        },
        {
            'question_text': 'What is the expected time complexity of randomized quicksort?',
            'option_a': 'O(n)',
            'option_b': 'O(n log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(n^1.5)',
            'correct_answer': 'B',
            'explanation': 'Randomized quicksort has expected time complexity O(n log n) with high probability.'
        },
        {
            'question_text': 'Design a parallel algorithm for mergesort. What is the speedup?',
            'option_a': 'Linear speedup O(n)',
            'option_b': 'Logarithmic speedup O(log n)',
            'option_c': 'Constant speedup',
            'option_d': 'Speedup depends on processor count',
            'correct_answer': 'B',
            'explanation': 'Parallel mergesort achieves O(log n) speedup when using n processors (log n depth).'
        },
    ],
    ('openai', 'easy'): [
        {
            'question_text': 'What is a neural network?',
            'option_a': 'A biological network of neurons',
            'option_b': 'A computational model inspired by biological neurons',
            'option_c': 'A type of database',
            'option_d': 'A computer network protocol',
            'correct_answer': 'B',
            'explanation': 'A neural network is a computational model inspired by biological neural networks in animal brains.'
        },
        {
            'question_text': 'What is the purpose of the activation function in neural networks?',
            'option_a': 'To turn neurons on or off',
            'option_b': 'To introduce non-linearity',
            'option_c': 'To normalize input values',
            'option_d': 'To increase computational speed',
            'correct_answer': 'B',
            'explanation': 'Activation functions introduce non-linearity, allowing neural networks to learn complex patterns.'
        },
        {
            'question_text': 'Which activation function outputs values between 0 and 1?',
            'option_a': 'ReLU',
            'option_b': 'Tanh',
            'option_c': 'Sigmoid',
            'option_d': 'Linear',
            'correct_answer': 'C',
            'explanation': 'Sigmoid function outputs values between 0 and 1: f(x) = 1 / (1 + e^(-x))'
        },
        {
            'question_text': 'What does backpropagation do?',
            'option_a': 'Forwards data through the network',
            'option_b': 'Updates weights by calculating gradients',
            'option_c': 'Initializes the network',
            'option_d': 'Normalizes input data',
            'correct_answer': 'B',
            'explanation': 'Backpropagation calculates gradients of the loss with respect to weights and updates them.'
        },
        {
            'question_text': 'What is the purpose of dropout in neural networks?',
            'option_a': 'To speed up training',
            'option_b': 'To prevent overfitting',
            'option_c': 'To improve accuracy',
            'option_d': 'To reduce memory usage',
            'correct_answer': 'B',
            'explanation': 'Dropout randomly deactivates neurons during training to prevent overfitting and co-adaptation.'
        },
        {
            'question_text': 'What is batch normalization?',
            'option_a': 'Normalizing entire dataset',
            'option_b': 'Normalizing each batch of data',
            'option_c': 'Normalizing network weights',
            'option_d': 'Normalizing output layer',
            'correct_answer': 'B',
            'explanation': 'Batch normalization normalizes inputs to each layer, improving training stability and speed.'
        },
        {
            'question_text': 'What is the role of loss function in neural networks?',
            'option_a': 'To store network weights',
            'option_b': 'To measure prediction error',
            'option_c': 'To normalize inputs',
            'option_d': 'To speed up computation',
            'correct_answer': 'B',
            'explanation': 'Loss function measures the difference between predicted and actual values.'
        },
        {
            'question_text': 'What is gradient descent?',
            'option_a': 'An optimization algorithm',
            'option_b': 'A way to initialize weights',
            'option_c': 'A data preprocessing technique',
            'option_d': 'A activation function',
            'correct_answer': 'A',
            'explanation': 'Gradient descent is an optimization algorithm that minimizes loss by updating weights in the direction of negative gradient.'
        },
        {
            'question_text': 'What is a convolutional layer in CNN?',
            'option_a': 'A fully connected layer',
            'option_b': 'A layer that applies filters to input',
            'option_c': 'A layer that reduces dimensions',
            'option_d': 'An activation layer',
            'correct_answer': 'B',
            'explanation': 'Convolutional layers apply filters (kernels) to input to extract features.'
        },
        {
            'question_text': 'What is max pooling?',
            'option_a': 'Averaging values in a window',
            'option_b': 'Taking maximum value in a window',
            'option_c': 'Concatenating feature maps',
            'option_d': 'Normalizing feature maps',
            'correct_answer': 'B',
            'explanation': 'Max pooling takes the maximum value from a window of values, reducing dimensions and preserving features.'
        },
        {
            'question_text': 'What is a recurrent neural network (RNN)?',
            'option_a': 'A network with cycles/feedback',
            'option_b': 'A fully connected network',
            'option_c': 'A convolutional network',
            'option_d': 'A network without hidden layers',
            'correct_answer': 'A',
            'explanation': 'RNNs have feedback connections allowing them to process sequential data.'
        },
        {
            'question_text': 'What is vanishing gradient problem?',
            'option_a': 'Gradients become too large',
            'option_b': 'Gradients become very small during backprop',
            'option_c': 'Network converges too fast',
            'option_d': 'Loss function is undefined',
            'correct_answer': 'B',
            'explanation': 'Vanishing gradient problem occurs when gradients become exponentially small in deep networks.'
        },
        {
            'question_text': 'What is LSTM?',
            'option_a': 'Long Short-Term Memory - a type of RNN',
            'option_b': 'A convolutional layer',
            'option_c': 'An optimization algorithm',
            'option_d': 'A loss function',
            'correct_answer': 'A',
            'explanation': 'LSTM (Long Short-Term Memory) is a type of RNN designed to handle long-term dependencies.'
        },
        {
            'question_text': 'What is attention mechanism?',
            'option_a': 'A way to focus on important parts of input',
            'option_b': 'An activation function',
            'option_c': 'A normalization technique',
            'option_d': 'A pooling operation',
            'correct_answer': 'A',
            'explanation': 'Attention mechanism allows the model to focus on relevant parts of the input when processing.'
        },
        {
            'question_text': 'What is a Transformer?',
            'option_a': 'A type of CNN',
            'option_b': 'A network architecture based on attention',
            'option_c': 'A type of RNN',
            'option_d': 'A data preprocessing tool',
            'correct_answer': 'B',
            'explanation': 'Transformers are neural network architectures based on self-attention, used in many NLP models.'
        },
        {
            'question_text': 'What is the purpose of embedding layer?',
            'option_a': 'To reduce dimensions',
            'option_b': 'To convert discrete inputs to dense vectors',
            'option_c': 'To increase network depth',
            'option_d': 'To normalize outputs',
            'correct_answer': 'B',
            'explanation': 'Embedding layers convert discrete inputs (like word indices) to dense vector representations.'
        },
        {
            'question_text': 'What is cross-entropy loss?',
            'option_a': 'Loss for regression tasks',
            'option_b': 'Loss function for classification tasks',
            'option_c': 'Loss for unsupervised learning',
            'option_d': 'A regularization technique',
            'correct_answer': 'B',
            'explanation': 'Cross-entropy loss measures the difference between predicted and true probability distributions for classification.'
        },
        {
            'question_text': 'What is overfitting?',
            'option_a': 'Model performs well on training data but poorly on test data',
            'option_b': 'Model performs poorly on both training and test data',
            'option_c': 'Model converges too slowly',
            'option_d': 'Model parameters are all zero',
            'correct_answer': 'A',
            'explanation': 'Overfitting occurs when a model learns training data too well including noise and cannot generalize.'
        },
        {
            'question_text': 'What is regularization?',
            'option_a': 'Making data normal distribution',
            'option_b': 'Technique to prevent overfitting',
            'option_c': 'Normalizing network outputs',
            'option_d': 'Initializing weights',
            'correct_answer': 'B',
            'explanation': 'Regularization techniques like L1/L2 add penalty terms to loss function to prevent overfitting.'
        },
        {
            'question_text': 'What is the purpose of validation set?',
            'option_a': 'To train the model',
            'option_b': 'To evaluate and tune model hyperparameters',
            'option_c': 'To test final model performance',
            'option_d': 'To initialize weights',
            'correct_answer': 'B',
            'explanation': 'Validation set is used to evaluate model performance and tune hyperparameters during training.'
        },
    ],
    ('uber', 'easy'): [
        {
            'question_text': 'What is API?',
            'option_a': 'Application Programming Interface - a way for software to communicate',
            'option_b': 'A type of database',
            'option_c': 'A programming language',
            'option_d': 'A testing framework',
            'correct_answer': 'A',
            'explanation': 'API is a set of protocols and tools for building software applications and specifying how software components interact.'
        },
        {
            'question_text': 'What does REST stand for?',
            'option_a': 'Representational State Transfer',
            'option_b': 'Remote End Server Terminal',
            'option_c': 'Reliable Electronic System Technology',
            'option_d': 'Request-Execution Synchronization',
            'correct_answer': 'A',
            'explanation': 'REST (Representational State Transfer) is an architectural style for designing networked applications.'
        },
        {
            'question_text': 'What are HTTP methods?',
            'option_a': 'GET, POST, PUT, DELETE, PATCH',
            'option_b': 'READ, WRITE, UPDATE',
            'option_c': 'REQUEST, RESPONSE',
            'option_d': 'CLIENT, SERVER',
            'correct_answer': 'A',
            'explanation': 'HTTP methods include GET (retrieve), POST (create), PUT (replace), DELETE (remove), PATCH (partial update).'
        },
        {
            'question_text': 'What is JSON?',
            'option_a': 'A database technology',
            'option_b': 'JavaScript Object Notation - a data format',
            'option_c': 'A programming language',
            'option_d': 'A network protocol',
            'correct_answer': 'B',
            'explanation': 'JSON is a lightweight data interchange format that is human-readable and widely used in APIs.'
        },
        {
            'question_text': 'What is caching?',
            'option_a': 'Storing frequently accessed data temporarily',
            'option_b': 'Compressing data',
            'option_c': 'Encrypting data',
            'option_d': 'Backing up data',
            'correct_answer': 'A',
            'explanation': 'Caching stores frequently accessed data in fast-access memory to improve performance.'
        },
        {
            'question_text': 'What is rate limiting?',
            'option_a': 'Limiting data transfer speed',
            'option_b': 'Limiting number of requests per time period',
            'option_c': 'Limiting user access',
            'option_d': 'Limiting server capacity',
            'correct_answer': 'B',
            'explanation': 'Rate limiting restricts the number of API requests a client can make in a given time period.'
        },
        {
            'question_text': 'What is load balancing?',
            'option_a': 'Balancing server weights',
            'option_b': 'Distributing requests across multiple servers',
            'option_c': 'Balancing database load',
            'option_d': 'Balancing network traffic',
            'correct_answer': 'B',
            'explanation': 'Load balancing distributes incoming requests across multiple servers to optimize resource use and performance.'
        },
        {
            'question_text': 'What is horizontal scaling?',
            'option_a': 'Increasing processor power',
            'option_b': 'Adding more servers/instances',
            'option_c': 'Increasing RAM',
            'option_d': 'Increasing database size',
            'correct_answer': 'B',
            'explanation': 'Horizontal scaling adds more machines/servers to a system, as opposed to vertical scaling which increases server power.'
        },
        {
            'question_text': 'What is microservices architecture?',
            'option_a': 'Large monolithic application',
            'option_b': 'Small, independent services that communicate',
            'option_c': 'Single database system',
            'option_d': 'One server handling all requests',
            'correct_answer': 'B',
            'explanation': 'Microservices is an architecture where applications are composed of small, independent services.'
        },
        {
            'question_text': 'What is containerization?',
            'option_a': 'Storing data in containers',
            'option_b': 'Packaging applications with dependencies',
            'option_c': 'Database technology',
            'option_d': 'Data compression',
            'correct_answer': 'B',
            'explanation': 'Containerization packages applications with their dependencies into isolated environments (like Docker).'
        },
        {
            'question_text': 'What is SQL injection?',
            'option_a': 'A performance optimization',
            'option_b': 'A security vulnerability where malicious SQL is injected',
            'option_c': 'A type of database query',
            'option_d': 'A backup technique',
            'correct_answer': 'B',
            'explanation': 'SQL injection is a security vulnerability where attackers inject malicious SQL code into input fields.'
        },
        {
            'question_text': 'What is authentication?',
            'option_a': 'Verifying user identity',
            'option_b': 'Authorizing user access',
            'option_c': 'Encrypting data',
            'option_d': 'Logging user activities',
            'correct_answer': 'A',
            'explanation': 'Authentication is the process of verifying that a user is who they claim to be.'
        },
        {
            'question_text': 'What is authorization?',
            'option_a': 'Verifying user identity',
            'option_b': 'Determining what an authenticated user can do',
            'option_c': 'Encrypting passwords',
            'option_d': 'Logging access',
            'correct_answer': 'B',
            'explanation': 'Authorization determines what resources an authenticated user is allowed to access.'
        },
        {
            'question_text': 'What is HTTPS?',
            'option_a': 'Regular HTTP',
            'option_b': 'HTTP with SSL/TLS encryption',
            'option_c': 'A faster version of HTTP',
            'option_d': 'A new HTTP protocol',
            'correct_answer': 'B',
            'explanation': 'HTTPS is HTTP with SSL/TLS encryption, providing secure communication over the internet.'
        },
        {
            'question_text': 'What is a database index?',
            'option_a': 'A list of all databases',
            'option_b': 'A data structure that improves query speed',
            'option_c': 'A backup of database',
            'option_d': 'A database version',
            'correct_answer': 'B',
            'explanation': 'An index is a database structure that speeds up data retrieval operations on a table.'
        },
        {
            'question_text': 'What is normalization in databases?',
            'option_a': 'Standardizing data format',
            'option_b': 'Organizing data to reduce redundancy',
            'option_c': 'Compressing database',
            'option_d': 'Backing up data',
            'correct_answer': 'B',
            'explanation': 'Database normalization organizes data to reduce redundancy and improve data integrity.'
        },
        {
            'question_text': 'What is ACID in databases?',
            'option_a': 'A programming language',
            'option_b': 'Properties ensuring reliable transactions: Atomicity, Consistency, Isolation, Durability',
            'option_c': 'A data format',
            'option_d': 'A backup strategy',
            'correct_answer': 'B',
            'explanation': 'ACID are properties that guarantee reliable database transactions and data integrity.'
        },
        {
            'question_text': 'What is eventually consistent?',
            'option_a': 'Data is always consistent',
            'option_b': 'Data becomes consistent after a delay',
            'option_c': 'Data never becomes consistent',
            'option_d': 'Consistency cannot be measured',
            'correct_answer': 'B',
            'explanation': 'Eventual consistency is a model where data is guaranteed to be consistent eventually, not immediately.'
        },
        {
            'question_text': 'What is a NoSQL database?',
            'option_a': 'Database without data',
            'option_b': 'Non-relational database with flexible schema',
            'option_c': 'Database without SQL',
            'option_d': 'Very fast database',
            'correct_answer': 'B',
            'explanation': 'NoSQL databases are non-relational and offer flexible schemas, useful for unstructured data.'
        },
        {
            'question_text': 'What is message queue?',
            'option_a': 'A list of messages',
            'option_b': 'A system for asynchronous communication between services',
            'option_c': 'A database table',
            'option_d': 'A email system',
            'correct_answer': 'B',
            'explanation': 'Message queue enables asynchronous communication by storing messages for processing by other services.'
        },
    ],
    ('microsoft', 'easy'): [
        {
            'question_text': 'What is C#?',
            'option_a': 'A music note',
            'option_b': 'A programming language by Microsoft',
            'option_c': 'A database',
            'option_d': 'A testing tool',
            'correct_answer': 'B',
            'explanation': 'C# is an object-oriented programming language developed by Microsoft for .NET framework.'
        },
        {
            'question_text': 'What is .NET Framework?',
            'option_a': 'A fishing net',
            'option_b': 'A software framework for building applications',
            'option_c': 'A network protocol',
            'option_d': 'A database system',
            'correct_answer': 'B',
            'explanation': '.NET Framework is a Microsoft software framework for building and running applications on Windows.'
        },
        {
            'question_text': 'What is Azure?',
            'option_a': 'A color',
            'option_b': 'A Microsoft cloud computing platform',
            'option_c': 'A database',
            'option_d': 'A programming language',
            'correct_answer': 'B',
            'explanation': 'Azure is Microsoft\'s cloud computing platform offering services like computing, storage, and analytics.'
        },
        {
            'question_text': 'What is LINQ?',
            'option_a': 'A data structure',
            'option_b': 'Language Integrated Query - for querying data',
            'option_c': 'A testing framework',
            'option_d': 'A debugging tool',
            'correct_answer': 'B',
            'explanation': 'LINQ is a Microsoft technology that integrates querying of data into C# language itself.'
        },
        {
            'question_text': 'What is ASP.NET?',
            'option_a': 'A programming language',
            'option_b': 'A web framework by Microsoft',
            'option_c': 'A database system',
            'option_d': 'A debugging tool',
            'correct_answer': 'B',
            'explanation': 'ASP.NET is a web application framework for building dynamic web pages and APIs.'
        },
        {
            'question_text': 'What is Entity Framework?',
            'option_a': 'A UI framework',
            'option_b': 'An ORM (Object-Relational Mapping) framework',
            'option_c': 'A testing framework',
            'option_d': 'A networking tool',
            'correct_answer': 'B',
            'explanation': 'Entity Framework is an ORM that allows developers to work with databases using .NET objects.'
        },
        {
            'question_text': 'What is WPF?',
            'option_a': 'Web programming framework',
            'option_b': 'Windows Presentation Foundation - for desktop applications',
            'option_c': 'A database system',
            'option_d': 'A networking protocol',
            'correct_answer': 'B',
            'explanation': 'WPF is a framework for building desktop applications with rich user interfaces on Windows.'
        },
        {
            'question_text': 'What is delegate in C#?',
            'option_a': 'A person who represents',
            'option_b': 'A type-safe function pointer',
            'option_c': 'A database query',
            'option_d': 'A control flow statement',
            'correct_answer': 'B',
            'explanation': 'A delegate in C# is a type-safe reference type representing a method with specific signature.'
        },
        {
            'question_text': 'What is async/await in C#?',
            'option_a': 'A looping construct',
            'option_b': 'A way to write asynchronous code synchronously',
            'option_c': 'A data structure',
            'option_d': 'A debugging feature',
            'correct_answer': 'B',
            'explanation': 'Async/await simplifies writing asynchronous code in C# making it read like synchronous code.'
        },
        {
            'question_text': 'What is Task in C#?',
            'option_a': 'Something to do',
            'option_b': 'An asynchronous operation',
            'option_c': 'A method',
            'option_d': 'A thread',
            'correct_answer': 'B',
            'explanation': 'Task represents an asynchronous operation that can be awaited, useful for async programming.'
        },
    ],
}


class Command(BaseCommand):
    help = 'Seed sample questions for interview tests'

    def handle(self, *args, **options):
        # Clear existing questions if needed
        Question.objects.all().delete()
        
        total_created = 0
        
        for (company, difficulty), questions_list in QUESTIONS_DATA.items():
            for idx, q_data in enumerate(questions_list, 1):
                question = Question.objects.create(
                    company=company,
                    difficulty=difficulty,
                    question_text=q_data['question_text'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation']
                )
                total_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {company.upper()} ({difficulty.upper()}) - Q{idx}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {total_created} questions!')
        )
        self.stdout.write(self.style.SUCCESS('Questions available for:'))
        self.stdout.write(self.style.SUCCESS('  - Google (Easy, Medium, Hard)'))
        self.stdout.write(self.style.SUCCESS('  - OpenAI (Easy, Medium, Hard)'))
        self.stdout.write(self.style.SUCCESS('  - Uber (Easy, Medium, Hard)'))
        self.stdout.write(self.style.SUCCESS('  - Microsoft (Easy, Medium, Hard)'))
