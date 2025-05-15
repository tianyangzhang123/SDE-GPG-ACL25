# SDE-GPG-ACL25

## 🧠 Towards Generating Controllable and Solvable Geometry Problems by Leveraging Symbolic Deduction Engine

This repository provides a description of the work accepted by **ACL 2025 (Industry Track)**:
**"Towards Generating Controllable and Solvable Geometry Problem by Leveraging Symbolic Deduction Engine"**.

We introduce **SDE-GPG**, a novel pipeline framework for automatically generating **readable**, **solvable**, and **controllable** geometry problems using a **symbolic deduction engine**. Unlike prior studies that focus on math word problems, our approach targets geometry—emphasizing formal language, spatial reasoning, and diagram generation.

### 📌 Key Features

* **Controllable Problem Generation**: Generate problems based on specified *knowledge points* and *difficulty level*.
* **Symbolic Reasoning**: Use a symbolic deduction engine to ensure **solvability** via logical deduction.
* **Multi-modal Outputs**: Automatically produce **natural language text** and **corresponding geometric diagrams**.
* **Quality Assurance**: Employ a **checking module** to filter problems by path completeness and difficulty consistency.

### 🧪 Evaluation

We evaluate our framework on two public datasets:

* **JGEX-AG-231** (Olympiad + textbook problems)
* **GeoQA** (real-world middle school exam questions)

Results show that **SDE-GPG** with quality checking significantly outperforms GPT-4o and other baselines on readability, solvability, and controllability metrics.

### 📂 Code & Data

**Code release coming soon.**
The repository will include:

* The full pipeline for SDE-GPG
* Knowledge point–to–definition mapping tables
* Template-based natural language generation scripts
* Auto diagram drawing tool
* Evaluation scripts and annotated datasets
