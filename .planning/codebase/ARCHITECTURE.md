# Architecture

## System Overview
The NY Tagging System is a hybrid web application designed for high-speed industrial packing and labeling. It follows a multi-tier architecture:

1.  **Frontend (UI)**: A Vue 3 single-page application that provides the operator interface for scanning and monitoring.
2.  **Backend (API)**: A FastAPI service that handles business logic, serial number generation, and database interactions.
3.  **Database (Persistence)**: Microsoft SQL Server storing master data (Customers, Products) and transaction logs (Cartons, Items).
4.  **Local Print Agent (Execution)**: A Python-based agent running on the client workstation to bypass browser security and interact directly with BarTender via COM.

## Hybrid Printing Workflow
To ensure reliable printing to local USB/Network printers without browser prompts:
-   **Server Role**: Generates a BarTender XML (BTXML) script containing all dynamic data (Item Name, S/N, QR Code).
-   **Frontend Role**: Receives the BTXML and relays it to the local agent's HTTP port (1234).
-   **Agent Role**: Receives the script, automates BarTender (COM), checks printer status, and triggers the physical print.

## Key Design Principles
-   **Concurrency Safety**: Uses `with_for_update()` on sequence generation to prevent duplicate Carton S/Ns in high-speed environments.
-   **Resilience**: The Print Agent logs all jobs locally to `C:\print_jobs` as an audit trail.
-   **Simplicity**: Uses a "Thin Backend" approach where most UI logic stays in the frontend.
