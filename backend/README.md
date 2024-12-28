

# 📊 Database Schema Overview

The database schema for NumeroNexus is meticulously designed to ensure normalization, scalability, and data integrity. The schema supports seamless relationships among various entities while optimizing performance for high-demand use cases.

---


### **Entity Relationship Diagram (ERD)**

📷 **[View ERD Diagram]![nexus_erd](https://github.com/user-attachments/assets/121fbd5e-2402-4939-b141-ff084089b40e)
(#)**  

---

### **Model Implementation**

💾 **([View `model.py` on GitHub](https://github.com/OfficialAshish/NumeroNexus_pub/blob/main/backend/app/models.py))**  


---

## **Schema Overview (Aligned with ERD)**

1. **Authenticated Users (`AuthUser`)**
   - Stores detailed information about authenticated users.
   - Key Relationships:
     - **Self Reports:** One-to-One relationship with `NumerologyReportAuth`.
     - **Friendships:** Many-to-Many relationship through the `friend_association` table.
     - **Friend Requests:** Managed via the `FriendRequest` table.

2. **Public Users (`User`)**
   - Represents non-authenticated users with minimal attributes: `name`, `dob`, and `gender`.
   - Reusability: Avoids duplication by reusing user data (e.g., common `dob` and `gender`) for multiple guest reports.

3. **Numerology Reports**
   - **Personal Reports (`NumerologyReportAuth`):** 
     - Linked to `AuthUser` for private, detailed reports.
     - Report data is stored in a JSON-based field (`report_data`) for flexibility.
   - **Public Reports (`NumerologyReport`):**
     - Linked to `User` with optional overrides for names using `person_name`.
     - Enables better organization when a single user is referenced multiple times via foreign keys.
   - **Shared Data (`SubReport`):**
     - Stores reusable JSON data (`dob`, `gender`) for multiple common reports.
     - Optimized with indexed fields for efficient querying.

4. **Compatibility Matching**
   - **Compatibility Reports (`CompatibilityReport`):**
     - Links two users with a shared `SubMatch` for compatibility data.
   - **Shared Compatibility Data (`SubMatch`):**
     - Stores reusable compatibility data in JSON format.
     - Optimized with indexed attributes for rapid retrieval.

5. **Auxiliary Features**
   - **Email Subscriptions (`EmailSubscription`):**
     - Tracks subscribed emails for newsletters or updates.
   - **Report Issues (`ReportIssues`):**
     - Logs and manages issues or complaints related to `NumerologyReport`.

---
