ℹ️ The above provided source code is a limited excerpt. 

---

# 🌟 **Introducing NumeroNexus**: Your Personalized Gateway to Numerology 🌌  

[**Start Exploring Now**](https://numeronexus.dedyn.io)  


---

## ⚙️ **Technology Stack**  

- **Frontend:** React.js with Tailwind CSS for a modern and responsive UI.  
- **Backend:** FastAPI for scalable, high-performance APIs.  
- **Database:** PostgreSQL with PostGIS for advanced geo-based queries.  
- **Caching Architecture:** On-device, Nginx, and Redis caching ensure blazing speed and reliability.  
- **Deployment:** Dockerized services hosted on AWS EC2 with Nginx for static file serving and RDS for database management.  

---

## 📂 **Key Features**  

 
### 🔍 **Advanced Report Filtering**  
Search and filter reports with precision using:  
- **Location-Based Search:** Filter by geographic location with customizable radius.  
- **Demographic Filters:** Filter by age range, gender, or whether reports have an associated Instagram/username.  
- **Personal Criteria:** Search by person name or specific birthday.  
- **Guest vs. Authorized Reports:** Distinguish between guest-generated and verified reports for detailed insights.  


### 🤝 **Friendship Connections**  
- Build connections with other authorized users to discover mutual friends and explore their reports along with compatibility insights.


### 📝 **Numerology Reports**  
- **User-Generated Reports:** View, organize, and manage all your created numerology reports.  
- **Saved Reports:** Access and analyze saved reports from other users effortlessly.  
- **AI Summaries:**  Reports feature AI-driven concise summaries for quick insights.  
- **Dynamic Compatibility Matches:** Logged-in users see auto-calculated compatibility matches for every report they view.  


###  **Compatibility Matching**  
- **Interactive Interface:** Enter details for two individuals or select from saved reports to analyze compatibility.  
- **Privacy-First:** Matches are private by default, accessible only via unique sharable links.  
- **Editable Anytime:** Revisit and modify compatibility details as needed.  
- **History Logs:** Easily access previous matches without needing to recreate them.  

---

## 🔒 **Security Features**  

1. **API Protection:**  
   - All backend APIs are rate-limited to prevent misuse and overloading.  
   - APIs are accessible **only** through the frontend; direct requests return a **403 Forbidden** response.  

2. **Nginx Security Measures:**  
   - Protects against **DDoS**, **CORS**, **XSS**, and other attacks.  
   - Efficiently serves and caches static frontend files and frequent backend requests.  

3. **JWT-Based Report Security:**  
   - Each user’s report has its own JWT, enabling on-device authentication for editing or deleting reports even without logging in.  
   - When users log in via **Auth0 (Okta)**, their reports sync with their account, making them accessible across devices.  

4. **Auth0 Integration:**  
   - Robust cookie-based session management for user security.  
   - Enforces email verification and restricts signup to recognized email domains (blocking disposable or temporary email addresses).  
   - Supports Google Sign-In via Auth0 for secure and convenient access. 

5. **Dynamic Multi-Layered Caching:**  
   - **On-Device Caching:** Provides offline access for critical data like filters and reports.  
   - **Nginx Caching:** Caches static files and frequently requested data for reduced latency.  
   - **Redis Backend Caching:** Dynamically caches real-time data for ultra-fast performance during operations.  

---

## 🚀 **Performance Highlights**  

1. **Blazing Speed:** Dynamic caching at every layer ensures lightning-fast responses and seamless experiences.  
2. **Scalability & Reliability:** Robust architecture handles high traffic while maintaining smooth performance.  
3. **Geo-Based Filtering:** Efficient and precise location-based filtering using PostGIS.  
4. **Dynamic Adaptation:** The caching system intelligently adapts to user behavior and requests for optimal performance.  

---


## 🌐 **Get Started with NumeroNexus**  

👉 **[Explore NumeroNexus](https://numeronexus.dedyn.io)**  
👉 [Terms of Use](https://numeronexus.dedyn.io/terms-of-use)  
👉 [Privacy Policy](https://numeronexus.dedyn.io/privacy-policy)  

---  
 
