A high-performance, asynchronous social media backend built for speed, security, and a touch of sarcasm.

### 🛠️ Tools
Framework: FastAPI (Async, High-Performance)

Data validation/ response modeling: Pydantic v2.0

Database: PostgreSQL with SQLAlchemy 2.0

Caching: Redis (JWT Blacklisting & Session Management)

AI Engine: Groq (LLaMA-3)

Authentication: JWT with Refresh Token Rotation


-----------------------------------------------------------------------------------------------------

### 🚀 Features
Advanced Auth: Secure login/registration with JWT. Implements Refresh Token Rotation to prevent session hijacking.

Optimized Performance: Uses Redis as a caching layer for active and blacklisted tokens.

Async CRUD: Full support for creating, liking, and updating posts using Python's async/await for high concurrency.

LLM Integration: Integrated with Groq to provide sarcastic summaries and Q&A on user posts.

Database Integrity: Utilizes SQLAlchemy 2.0's latest patterns for type-safe database interactions.

