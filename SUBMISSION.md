# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `Dockerfile.fast`: the fast build
- [ ] `.dockerignore`

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste the output of `./measure.sh` for the slow Dockerfile (cold build, then a one-line source change). Which step took the time on the second build, and why did Docker not reuse it?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Explain the cache rule in your own words: when does Docker reuse a layer and when does it throw away that layer and every layer after it? Which instruction in `Dockerfile.slow` broke the chain?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. Paste the line `transferring context` for the slow and for the fast build. What is the build context, why does a large one slow every build, and what does `.dockerignore` change?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Paste `./measure.sh` for your Dockerfile. How much faster is the rebuild after a source change? And after a change to `requirements.txt`? Why is the second one allowed to be slow?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. What does `RUN --mount=type=cache,target=/root/.cache/pip` do that `pip install --no-cache-dir` does not? When does the cache mount NOT help (hint: CI runners that start empty), and what could you use there?

**Your answer:**

<!-- replace this line with your answer -->

### Q6. Why must `apt-get update` and `apt-get install` be in the same `RUN`? Show the failure you get otherwise a few weeks later.

**Your answer:**

<!-- replace this line with your answer -->

### Q7. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q8. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
