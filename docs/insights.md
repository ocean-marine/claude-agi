# Insights on Python Coding Styles Suited for Generative AI

During a brief exploration of online resources on *generative AI and Python*, we encountered limited access to some sites, receiving responses such as `Upgrade Required`. As a result, we relied on general knowledge about effective styles when using generative models for code generation.

Key points:

- **Small modular functions** with clear responsibilities are easier for AI models to generate and understand.
- **Descriptive naming** and **type hints** help the model maintain consistency across code blocks.
- **Docstrings** and inline comments provide useful context, guiding the model when extending or modifying code.
- Leveraging **standard libraries** (e.g., `argparse` for CLI tools) avoids unnecessary complexity.

To apply these practices, we implemented a minimal CLI TODO application demonstrating this style.
