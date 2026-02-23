# FarPay: Secure Payment & Settlement Demo
**Developed by:** Martin Wachira  
**Target Organization:** Farsight Africa Group – ICT Department  
**Stack:** Android (Java), FastAPI (Python), PostgreSQL

---

## 1. Project Overview
FarPay is a proof-of-concept mobile payment application designed to demonstrate a secure, end-to-end transaction lifecycle. The system facilitates merchant payments via Pesapal, Visa/Mastercard (Tokenized), and Mock Bank transfers. The core focus of this implementation is **transaction integrity**, **PCI DSS compliance**, and **fault tolerance**.

## 2. Technical Architecture
The system follows a decoupled, N-tier architecture to ensure clear separation of concerns:

* **Mobile Frontend (Android/Java):** Handles the presentation layer and secure local caching. It follows the **MVVM (Model-View-ViewModel)** pattern to ensure UI responsiveness.
* **Backend API (FastAPI/Python):** Acts as the secure orchestrator. It manages all sensitive communication with payment gateways and enforces business logic.
* **Database (PostgreSQL):** Serves as the immutable source of truth for transaction states and user audit trails.
* **External Integration:** Utilizes Pesapal Sandbox for payment simulation and **Ngrok** for handling asynchronous IPN (Instant Payment Notification) callbacks in a local development environment.

## 3. Core Features & Implementation Details

### A. Secure Payment Flow (PCI DSS Alignment)
To ensure sensitive card data never touches our infrastructure, the following measures are implemented:
* **Webview Interception:** Card details are entered via a secure gateway-hosted Webview provided by Pesapal.
* **Tokenization:** The mobile client receives a non-sensitive payment token/tracking ID. The backend uses this ID to query status, ensuring the "scope of impact" is limited in case of a breach.

### B. Transaction Resilience
* **Status Polling:** The app implements a background polling mechanism to check the backend status, ensuring the UI stays synchronized with the database regardless of callback delays.

