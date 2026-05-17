# Agent Instructions for Robotics Landscape Project

## Project Overview
This is a purely front-end generic Knowledge / Landscape viewer built for the Robotics (Embodied AI) domain. It is designed to be hosted on static hosting like GitHub Pages, meaning there is **no database** or backend server.

## Data Storage & Architecture
The data is stored as static JSON files in the `public/data/` directory to allow easy modular updates without needing to recompile the TypeScript application. 

### Data Update Rules for Agents
When instructed to add, remove, or modify robotics information or entities, **DO NOT** edit `src/data/entities.ts` to add data. Instead, you must edit the appropriate JSON file in `public/data/`:

*   **`public/data/index.json`**: The manifest file. Only edit this if adding a completely new data partition.
*   **`public/data/hardware.json`**: Hardware related entities. Categories: `整机平台`, `机械臂`, `灵巧手 & 夹爪`, `关节模组`, `核心零部件`, `传感器`, `能源动力`, `数采 & 遥操`, `计算平台`.
*   **`public/data/software.json`**: Software related entities. Categories: `基础模型`, `算法框架`, `控制算法`, `仿真平台`, `数据集`, `评测基准`.
*   **`public/data/ecosystem.json`**: Ecosystem & Applications. Categories: `开发生态`, `应用场景`.
*   **`public/data/players.json`**: Involved Entities (参与实体). Categories: `资本`, `产业`, `实验室`.

When searching for information or inserting new entities, ensure the `category`, `id`, and structured data (such as `specs`, `tags`, `year`) precisely match the TypeScript interface `Entity` defined in `src/data/entities.ts`.

## UI & Component Boundaries
The project is built with React, Tailwind CSS, and `motion` (Framer Motion). 

*   **`src/App.tsx`**: Main orchestrator. Controls navigation state (`mainTab`, selected `activeCategory`), and orchestrates the layout. Avoid putting complex UI logic here; extract to components if it scales.
*   **`src/components/TimelineView.tsx`**: Renders the "演进脉络" (Evolution Timeline). Groups entities by `year`.
*   **`src/components/GridView.tsx`**: Renders the "全景架构" (Overall Architecture Grid).
*   **`src/components/WheelSelector.tsx`**: Used in specific category views allowing users to spin through items via mouse wheel.
*   **`src/components/EntityCard.tsx`**: Renders a card for a given `Entity`.
*   **`src/components/SingleSpecsPanel.tsx`**: Renders the detailed view (tags, specs, paper info) for a selected entity.
*   **`src/data/entities.ts`**: Contains **ONLY** the TypeScript typings (`Entity`, `Category`, `TopLevelGroup`) and the fetching logic (`loadEntities`). **DO NOT** hardcode mock data here.

## Styling Guidelines
*   Use standard Tailwind CSS utility classes.
*   Design is precision-driven (uses exact spacing like `w-[480px]`, `h-[720px]`). Maintain consistent dimensions or update them universally across components if a resize is requested.
*   All animations MUST use `motion` from `motion/react`.

## Important Note to Agents
If you receive instructions that conflict with these definitions, assume the user is asking to bend or change the rules, but ALWAYS verify first. If the user asks for a simple data entry task, just update the JSON file via Node scripts or file edits. Do not over-engineer.
