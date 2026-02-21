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
* **Idempotency Keys:** Every transaction initiation generates a unique `idempotency_key`. This prevents double-charging if a user accidentally taps the "Pay" button twice or if the network retries a request.
* **Status Polling:** The app implements a background polling mechanism to check the backend status, ensuring the UI stays synchronized with the database regardless of callback delays.

### C. Offline Capability & Local Storage
* **Room Persistence:** Past transactions are cached in a local **Room Database**. Users can view their transaction history without an active internet connection.
* **Encrypted Preferences:** Sensitive identifiers, such as Auth Tokens and API keys, are stored using **EncryptedSharedPreferences** via the Android Keystore.

### D. Document Generation
* Successful transactions trigger a PDF receipt generator using the `PdfDocument` API, providing users with immediate, downloadable proof of payment.

## 4. Database Schema
The PostgreSQL database utilizes a `transactions` table with the following critical fields:
* `transaction_id`: Primary Key (UUID)
* `pesapal_tracking_id`: Gateway reference for reconciliation.
* `amount`: Decimal (Fixed point for precision).
* `status`: (PENDING, SUCCESS, FAILED).
* `idempotency_key`: Unique constraint to prevent duplicate processing.
* `created_at`: Timestamp for audit logs.

## 5. Security Protocols
* **Environment Variables:** No API keys or Database credentials are hardcoded. All secrets are managed via `.env` files.
* **Signature Verification:** The backend is designed to verify the signature of all incoming IPNs to prevent Request Spoofing.
* **SSL/TLS:** Communication between the mobile client and the API is handled over HTTPS (tunneled via Ngrok).

## 6. Setup & Installation

### Backend (Python/FastAPI)
1. Navigate to `/backend`.
2. Create virtual environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Configure `.env` with PostgreSQL credentials and Pesapal Sandbox keys.
5. Run server: `uvicorn main:app --reload`.
6. Start Ngrok: `ngrok http 8000` (Update Pesapal Dashboard with the Ngrok URL).

### Mobile (Android/Java)
1. Open the project in Android Studio.
2. Update the `BASE_URL` in the Retrofit client with your active Ngrok address.
3. Sync Gradle and run the app.

## 7. Quality Assurance (QA)
* **Unit Testing:** Logic for amount validation is tested via **JUnit**.
* **Integration Testing:** Payment flow from Mobile -> Backend -> Database verified using **Postman**.
* **Failure Scenarios Tested:** * Network timeout during processing.
    * Declined card responses.
    * Simulated gateway downtime (503 errors).
