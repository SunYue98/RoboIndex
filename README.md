# Embodied AI Landscape (具身智能系统架构与演进)

An interactive, purely front-end knowledge graph and landscape visualization tool for the Robotics and Embodied AI industry. 

## Features

*   **Static Hosting Ready**: Designed to run seamlessly on GitHub Pages, Vercel, or any static file server without requiring a database backend.
*   **Modular Data Fetching**: Data is decoupled from the source code. Information about hardware, software, and ecosystems is stored as easily readable and editable JSON files in the `/public/data/` directory.
*   **Interactive Visualizations**: View the industry through various lenses:
    *   **Architecture Grid (全景架构)**: A top-down look into Top-Level Groups (Hardware, Software, Ecosystem).
    *   **Timeline View (演进脉络)**: Track the progression of platforms, algorithms, and models linearly by year.
    *   **Category Deep-Dives**: Interactive wheel selectors for Hardware, Software, and Ecosystem components.
*   **Smooth Animations**: Powered by `motion/react` for buttery smooth layout transitions and interactions.

## Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Updating Data

To add new robots, models, or companies, you do not need to rebuild the project. Edit the files located in `public/data/`:
*   `hardware.json`
*   `software.json`
*   `ecosystem.json`

Ensure new entries follow the schema defined in `src/data/entities.ts`.

## Agent Maintainer Documentation

For AI Agents interacting with this repository, please consult [`AGENTS.md`](./AGENTS.md) for strict architectural boundaries, data partitioning strategies, and UI guidelines to prevent context pollution and structural regressions.
